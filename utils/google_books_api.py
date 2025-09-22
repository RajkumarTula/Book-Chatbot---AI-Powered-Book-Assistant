"""
Google Books API integration with Redis caching for sub-200ms response times.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

import httpx
import redis
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BookInfo:
    """Data class for book information."""
    title: str
    authors: List[str]
    publisher: str
    published_date: str
    description: str
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    page_count: Optional[int] = None
    categories: List[str] = None
    average_rating: Optional[float] = None
    ratings_count: Optional[int] = None
    price: Optional[float] = None
    currency: str = "USD"
    availability: str = "unknown"
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    language: str = "en"
    maturity_rating: str = "NOT_MATURE"

class GoogleBooksAPI:
    """Google Books API client with Redis caching for optimal performance."""
    
    def __init__(self, api_key: str = None, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """
        Initialize Google Books API client.
        
        Args:
            api_key: Google Books API key (optional, but recommended for higher rate limits)
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
        """
        self.api_key = api_key
        self.service = build('books', 'v1', developerKey=api_key) if api_key else build('books', 'v1')
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
        
        # Cache settings
        self.cache_ttl = 3600  # 1 hour
        self.search_cache_ttl = 1800  # 30 minutes for search results
        
    def _get_cache_key(self, operation: str, **kwargs) -> str:
        """Generate cache key for operation."""
        key_parts = [operation]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{str(v).lower()}")
        return ":".join(key_parts)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from Redis cache."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        return None
    
    def _set_cache(self, cache_key: str, data: Any, ttl: int = None) -> None:
        """Set data in Redis cache."""
        if not self.redis_client:
            return
        
        try:
            ttl = ttl or self.cache_ttl
            self.redis_client.setex(cache_key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def _parse_book_data(self, item: Dict) -> BookInfo:
        """Parse Google Books API response item to BookInfo."""
        volume_info = item.get('volumeInfo', {})
        sale_info = item.get('saleInfo', {})
        
        # Extract ISBNs
        isbn_10 = None
        isbn_13 = None
        for identifier in volume_info.get('industryIdentifiers', []):
            if identifier.get('type') == 'ISBN_10':
                isbn_10 = identifier.get('identifier')
            elif identifier.get('type') == 'ISBN_13':
                isbn_13 = identifier.get('identifier')
        
        # Extract price information
        price = None
        currency = "USD"
        if sale_info.get('listPrice'):
            price = sale_info['listPrice'].get('amount')
            currency = sale_info['listPrice'].get('currencyCode', 'USD')
        
        # Determine availability
        availability = "unknown"
        if sale_info.get('saleability') == 'FOR_SALE':
            availability = "available"
        elif sale_info.get('saleability') == 'NOT_FOR_SALE':
            availability = "not_available"
        
        return BookInfo(
            title=volume_info.get('title', 'Unknown Title'),
            authors=volume_info.get('authors', []),
            publisher=volume_info.get('publisher', 'Unknown Publisher'),
            published_date=volume_info.get('publishedDate', 'Unknown Date'),
            description=volume_info.get('description', 'No description available'),
            isbn_10=isbn_10,
            isbn_13=isbn_13,
            page_count=volume_info.get('pageCount'),
            categories=volume_info.get('categories', []),
            average_rating=volume_info.get('averageRating'),
            ratings_count=volume_info.get('ratingsCount'),
            price=price,
            currency=currency,
            availability=availability,
            thumbnail_url=volume_info.get('imageLinks', {}).get('thumbnail'),
            preview_url=volume_info.get('previewLink'),
            language=volume_info.get('language', 'en'),
            maturity_rating=volume_info.get('maturityRating', 'NOT_MATURE')
        )
    
    async def search_books(self, query: str, max_results: int = 10, start_index: int = 0) -> List[BookInfo]:
        """
        Search for books using Google Books API with caching.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            start_index: Starting index for pagination
            
        Returns:
            List of BookInfo objects
        """
        start_time = time.time()
        cache_key = self._get_cache_key("search", query=query, max_results=max_results, start_index=start_index)
        
        # Try to get from cache first
        cached_results = self._get_from_cache(cache_key)
        if cached_results:
            logger.info(f"Cache hit for search query: {query}")
            return [BookInfo(**book_data) for book_data in cached_results]
        
        try:
            # Make API request
            request = self.service.volumes().list(
                q=query,
                maxResults=min(max_results, 40),  # Google Books API limit
                startIndex=start_index,
                printType='books',
                orderBy='relevance'
            )
            
            response = request.execute()
            items = response.get('items', [])
            
            books = []
            for item in items:
                try:
                    book_info = self._parse_book_data(item)
                    books.append(book_info)
                except Exception as e:
                    logger.warning(f"Error parsing book data: {e}")
                    continue
            
            # Cache the results
            self._set_cache(cache_key, [book.__dict__ for book in books], self.search_cache_ttl)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Search completed in {elapsed_time:.3f}s, found {len(books)} books")
            
            return books
            
        except HttpError as e:
            logger.error(f"Google Books API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return []
    
    async def get_book_by_isbn(self, isbn: str) -> Optional[BookInfo]:
        """
        Get book information by ISBN with caching.
        
        Args:
            isbn: ISBN-10 or ISBN-13
            
        Returns:
            BookInfo object or None if not found
        """
        start_time = time.time()
        cache_key = self._get_cache_key("isbn", isbn=isbn)
        
        # Try to get from cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"Cache hit for ISBN: {isbn}")
            return BookInfo(**cached_result)
        
        try:
            # Search by ISBN
            request = self.service.volumes().list(q=f"isbn:{isbn}")
            response = request.execute()
            items = response.get('items', [])
            
            if items:
                book_info = self._parse_book_data(items[0])
                # Cache the result
                self._set_cache(cache_key, book_info.__dict__)
                
                elapsed_time = time.time() - start_time
                logger.info(f"ISBN lookup completed in {elapsed_time:.3f}s")
                
                return book_info
            
            return None
            
        except HttpError as e:
            logger.error(f"Google Books API error for ISBN {isbn}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during ISBN lookup: {e}")
            return None
    
    async def get_book_by_title(self, title: str) -> Optional[BookInfo]:
        """
        Get book information by exact title with caching.
        
        Args:
            title: Book title
            
        Returns:
            BookInfo object or None if not found
        """
        start_time = time.time()
        cache_key = self._get_cache_key("title", title=title)
        
        # Try to get from cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"Cache hit for title: {title}")
            return BookInfo(**cached_result)
        
        try:
            # Search by title
            request = self.service.volumes().list(q=f'intitle:"{title}"')
            response = request.execute()
            items = response.get('items', [])
            
            if items:
                book_info = self._parse_book_data(items[0])
                # Cache the result
                self._set_cache(cache_key, book_info.__dict__)
                
                elapsed_time = time.time() - start_time
                logger.info(f"Title lookup completed in {elapsed_time:.3f}s")
                
                return book_info
            
            return None
            
        except HttpError as e:
            logger.error(f"Google Books API error for title {title}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during title lookup: {e}")
            return None
    
    async def get_books_by_author(self, author: str, max_results: int = 10) -> List[BookInfo]:
        """
        Get books by author with caching.
        
        Args:
            author: Author name
            max_results: Maximum number of results
            
        Returns:
            List of BookInfo objects
        """
        start_time = time.time()
        cache_key = self._get_cache_key("author", author=author, max_results=max_results)
        
        # Try to get from cache first
        cached_results = self._get_from_cache(cache_key)
        if cached_results:
            logger.info(f"Cache hit for author: {author}")
            return [BookInfo(**book_data) for book_data in cached_results]
        
        try:
            # Search by author
            request = self.service.volumes().list(
                q=f'inauthor:"{author}"',
                maxResults=min(max_results, 40),
                orderBy='relevance'
            )
            response = request.execute()
            items = response.get('items', [])
            
            books = []
            for item in items:
                try:
                    book_info = self._parse_book_data(item)
                    books.append(book_info)
                except Exception as e:
                    logger.warning(f"Error parsing book data: {e}")
                    continue
            
            # Cache the results
            self._set_cache(cache_key, [book.__dict__ for book in books], self.search_cache_ttl)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Author search completed in {elapsed_time:.3f}s, found {len(books)} books")
            
            return books
            
        except HttpError as e:
            logger.error(f"Google Books API error for author {author}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during author search: {e}")
            return []
    
    async def get_books_by_genre(self, genre: str, max_results: int = 10) -> List[BookInfo]:
        """
        Get books by genre/category with caching.
        
        Args:
            genre: Genre or category
            max_results: Maximum number of results
            
        Returns:
            List of BookInfo objects
        """
        start_time = time.time()
        cache_key = self._get_cache_key("genre", genre=genre, max_results=max_results)
        
        # Try to get from cache first
        cached_results = self._get_from_cache(cache_key)
        if cached_results:
            logger.info(f"Cache hit for genre: {genre}")
            return [BookInfo(**book_data) for book_data in cached_results]
        
        try:
            # Search by subject/category
            request = self.service.volumes().list(
                q=f'subject:"{genre}"',
                maxResults=min(max_results, 40),
                orderBy='relevance'
            )
            response = request.execute()
            items = response.get('items', [])
            
            books = []
            for item in items:
                try:
                    book_info = self._parse_book_data(item)
                    books.append(book_info)
                except Exception as e:
                    logger.warning(f"Error parsing book data: {e}")
                    continue
            
            # Cache the results
            self._set_cache(cache_key, [book.__dict__ for book in books], self.search_cache_ttl)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Genre search completed in {elapsed_time:.3f}s, found {len(books)} books")
            
            return books
            
        except HttpError as e:
            logger.error(f"Google Books API error for genre {genre}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during genre search: {e}")
            return []
    
    async def get_bestsellers(self, max_results: int = 10) -> List[BookInfo]:
        """
        Get bestseller books with caching.
        
        Args:
            max_results: Maximum number of results
            
        Returns:
            List of BookInfo objects
        """
        start_time = time.time()
        cache_key = self._get_cache_key("bestsellers", max_results=max_results)
        
        # Try to get from cache first
        cached_results = self._get_from_cache(cache_key)
        if cached_results:
            logger.info("Cache hit for bestsellers")
            return [BookInfo(**book_data) for book_data in cached_results]
        
        try:
            # Search for popular books
            request = self.service.volumes().list(
                q='bestseller OR popular OR trending',
                maxResults=min(max_results, 40),
                orderBy='relevance'
            )
            response = request.execute()
            items = response.get('items', [])
            
            books = []
            for item in items:
                try:
                    book_info = self._parse_book_data(item)
                    books.append(book_info)
                except Exception as e:
                    logger.warning(f"Error parsing book data: {e}")
                    continue
            
            # Cache the results
            self._set_cache(cache_key, [book.__dict__ for book in books], self.search_cache_ttl)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Bestsellers search completed in {elapsed_time:.3f}s, found {len(books)} books")
            
            return books
            
        except HttpError as e:
            logger.error(f"Google Books API error for bestsellers: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during bestsellers search: {e}")
            return []
    
    async def get_new_releases(self, max_results: int = 10) -> List[BookInfo]:
        """
        Get new release books with caching.
        
        Args:
            max_results: Maximum number of results
            
        Returns:
            List of BookInfo objects
        """
        start_time = time.time()
        cache_key = self._get_cache_key("new_releases", max_results=max_results)
        
        # Try to get from cache first
        cached_results = self._get_from_cache(cache_key)
        if cached_results:
            logger.info("Cache hit for new releases")
            return [BookInfo(**book_data) for book_data in cached_results]
        
        try:
            # Search for recent books (last 2 years)
            current_year = datetime.now().year
            search_query = f'publishedDate:>{current_year-2}'
            
            request = self.service.volumes().list(
                q=search_query,
                maxResults=min(max_results, 40),
                orderBy='newest'
            )
            response = request.execute()
            items = response.get('items', [])
            
            books = []
            for item in items:
                try:
                    book_info = self._parse_book_data(item)
                    books.append(book_info)
                except Exception as e:
                    logger.warning(f"Error parsing book data: {e}")
                    continue
            
            # Cache the results
            self._set_cache(cache_key, [book.__dict__ for book in books], self.search_cache_ttl)
            
            elapsed_time = time.time() - start_time
            logger.info(f"New releases search completed in {elapsed_time:.3f}s, found {len(books)} books")
            
            return books
            
        except HttpError as e:
            logger.error(f"Google Books API error for new releases: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during new releases search: {e}")
            return []

# Global instance
google_books_api = GoogleBooksAPI()

# Convenience functions
async def search_books(query: str, max_results: int = 10) -> List[BookInfo]:
    """Search for books."""
    return await google_books_api.search_books(query, max_results)

async def get_book_by_title(title: str) -> Optional[BookInfo]:
    """Get book by title."""
    return await google_books_api.get_book_by_title(title)

async def get_book_by_isbn(isbn: str) -> Optional[BookInfo]:
    """Get book by ISBN."""
    return await google_books_api.get_book_by_isbn(isbn)

async def get_books_by_author(author: str, max_results: int = 10) -> List[BookInfo]:
    """Get books by author."""
    return await google_books_api.get_books_by_author(author, max_results)

async def get_books_by_genre(genre: str, max_results: int = 10) -> List[BookInfo]:
    """Get books by genre."""
    return await google_books_api.get_books_by_genre(genre, max_results)

async def get_bestsellers(max_results: int = 10) -> List[BookInfo]:
    """Get bestseller books."""
    return await google_books_api.get_bestsellers(max_results)

async def get_new_releases(max_results: int = 10) -> List[BookInfo]:
    """Get new release books."""
    return await google_books_api.get_new_releases(max_results)

