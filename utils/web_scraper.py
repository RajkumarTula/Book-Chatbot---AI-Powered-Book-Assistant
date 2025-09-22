"""
Web scraping utilities using BeautifulSoup4 for additional book information.
"""

import asyncio
import logging
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from urllib.parse import urljoin, quote
import time

import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BookReview:
    """Data class for book reviews."""
    reviewer_name: str
    rating: float
    review_text: str
    review_date: str
    source: str

@dataclass
class BookstoreInfo:
    """Data class for bookstore information."""
    store_name: str
    price: float
    currency: str
    availability: str
    url: str
    shipping_info: str = ""

class BookWebScraper:
    """Web scraper for additional book information."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the web scraper.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.session = None
        self.driver = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def initialize(self):
        """Initialize the scraper."""
        try:
            # Initialize HTTP session
            self.session = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            
            # Initialize Selenium driver if needed
            if self.headless:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                
                self.driver = webdriver.Chrome(options=chrome_options)
            else:
                self.driver = webdriver.Chrome()
            
            logger.info("Web scraper initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing web scraper: {e}")
            raise
    
    async def close(self):
        """Close the scraper resources."""
        try:
            if self.session:
                await self.session.aclose()
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.warning(f"Error closing scraper: {e}")
    
    async def scrape_goodreads_reviews(self, book_title: str, author: str = None, max_reviews: int = 10) -> List[BookReview]:
        """
        Scrape book reviews from Goodreads.
        
        Args:
            book_title: Book title
            author: Book author (optional)
            max_reviews: Maximum number of reviews to scrape
            
        Returns:
            List of BookReview objects
        """
        try:
            # Construct search URL
            search_query = f"{book_title}"
            if author:
                search_query += f" {author}"
            
            search_url = f"https://www.goodreads.com/search?q={quote(search_query)}"
            
            # Get search results page
            response = await self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the first book result
            book_link = None
            book_elements = soup.find_all('a', class_='bookTitle')
            if book_elements:
                book_link = urljoin(search_url, book_elements[0]['href'])
            
            if not book_link:
                logger.warning(f"No book found on Goodreads for: {book_title}")
                return []
            
            # Get book page
            book_response = await self.session.get(book_link)
            book_response.raise_for_status()
            
            book_soup = BeautifulSoup(book_response.content, 'html.parser')
            
            # Scrape reviews
            reviews = []
            review_elements = book_soup.find_all('div', class_='review')
            
            for review_elem in review_elements[:max_reviews]:
                try:
                    # Get reviewer name
                    reviewer_name = "Unknown"
                    name_elem = review_elem.find('a', class_='user')
                    if name_elem:
                        reviewer_name = name_elem.get_text(strip=True)
                    
                    # Get rating
                    rating = 0.0
                    rating_elem = review_elem.find('span', class_='staticStars')
                    if rating_elem:
                        rating_text = rating_elem.get('title', '')
                        rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                    
                    # Get review text
                    review_text = ""
                    text_elem = review_elem.find('div', class_='reviewText')
                    if text_elem:
                        review_text = text_elem.get_text(strip=True)
                    
                    # Get review date
                    review_date = "Unknown"
                    date_elem = review_elem.find('a', class_='reviewDate')
                    if date_elem:
                        review_date = date_elem.get_text(strip=True)
                    
                    if review_text:  # Only add reviews with text
                        review = BookReview(
                            reviewer_name=reviewer_name,
                            rating=rating,
                            review_text=review_text,
                            review_date=review_date,
                            source="Goodreads"
                        )
                        reviews.append(review)
                
                except Exception as e:
                    logger.warning(f"Error parsing review: {e}")
                    continue
            
            logger.info(f"Scraped {len(reviews)} reviews from Goodreads for {book_title}")
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping Goodreads reviews: {e}")
            return []
    
    async def scrape_amazon_prices(self, book_title: str, author: str = None) -> List[BookstoreInfo]:
        """
        Scrape book prices from Amazon.
        
        Args:
            book_title: Book title
            author: Book author (optional)
            
        Returns:
            List of BookstoreInfo objects
        """
        try:
            # Construct search URL
            search_query = f"{book_title}"
            if author:
                search_query += f" {author}"
            
            search_url = f"https://www.amazon.com/s?k={quote(search_query)}&i=stripbooks"
            
            # Use Selenium for Amazon (they have anti-bot measures)
            self.driver.get(search_url)
            
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))
            )
            
            # Parse results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            bookstore_infos = []
            result_elements = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for result_elem in result_elements[:5]:  # Limit to first 5 results
                try:
                    # Get book title
                    title_elem = result_elem.find('h2', class_='a-size-mini')
                    if not title_elem:
                        continue
                    
                    book_title_text = title_elem.get_text(strip=True)
                    
                    # Get price
                    price = None
                    price_elem = result_elem.find('span', class_='a-price-whole')
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price = float(price_text.replace(',', ''))
                    
                    # Get availability
                    availability = "Unknown"
                    availability_elem = result_elem.find('span', class_='a-color-base')
                    if availability_elem:
                        availability = availability_elem.get_text(strip=True)
                    
                    # Get product URL
                    product_url = ""
                    link_elem = result_elem.find('h2', class_='a-size-mini').find('a')
                    if link_elem:
                        product_url = urljoin(search_url, link_elem['href'])
                    
                    if price:
                        bookstore_info = BookstoreInfo(
                            store_name="Amazon",
                            price=price,
                            currency="USD",
                            availability=availability,
                            url=product_url,
                            shipping_info="Free shipping on orders over $25"
                        )
                        bookstore_infos.append(bookstore_info)
                
                except Exception as e:
                    logger.warning(f"Error parsing Amazon result: {e}")
                    continue
            
            logger.info(f"Scraped {len(bookstore_infos)} price listings from Amazon for {book_title}")
            return bookstore_infos
            
        except Exception as e:
            logger.error(f"Error scraping Amazon prices: {e}")
            return []
    
    async def scrape_barnes_noble_prices(self, book_title: str, author: str = None) -> List[BookstoreInfo]:
        """
        Scrape book prices from Barnes & Noble.
        
        Args:
            book_title: Book title
            author: Book author (optional)
            
        Returns:
            List of BookstoreInfo objects
        """
        try:
            # Construct search URL
            search_query = f"{book_title}"
            if author:
                search_query += f" {author}"
            
            search_url = f"https://www.barnesandnoble.com/s/{quote(search_query)}"
            
            # Get search results page
            response = await self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            bookstore_infos = []
            result_elements = soup.find_all('div', class_='product-shelf-item')
            
            for result_elem in result_elements[:5]:  # Limit to first 5 results
                try:
                    # Get book title
                    title_elem = result_elem.find('h3', class_='product-info-title')
                    if not title_elem:
                        continue
                    
                    book_title_text = title_elem.get_text(strip=True)
                    
                    # Get price
                    price = None
                    price_elem = result_elem.find('span', class_='current')
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price_match = re.search(r'\$(\d+(?:\.\d+)?)', price_text)
                        if price_match:
                            price = float(price_match.group(1))
                    
                    # Get availability
                    availability = "Unknown"
                    availability_elem = result_elem.find('span', class_='availability')
                    if availability_elem:
                        availability = availability_elem.get_text(strip=True)
                    
                    # Get product URL
                    product_url = ""
                    link_elem = result_elem.find('a', class_='product-info-title')
                    if link_elem:
                        product_url = urljoin(search_url, link_elem['href'])
                    
                    if price:
                        bookstore_info = BookstoreInfo(
                            store_name="Barnes & Noble",
                            price=price,
                            currency="USD",
                            availability=availability,
                            url=product_url,
                            shipping_info="Free shipping on orders over $40"
                        )
                        bookstore_infos.append(bookstore_info)
                
                except Exception as e:
                    logger.warning(f"Error parsing Barnes & Noble result: {e}")
                    continue
            
            logger.info(f"Scraped {len(bookstore_infos)} price listings from Barnes & Noble for {book_title}")
            return bookstore_infos
            
        except Exception as e:
            logger.error(f"Error scraping Barnes & Noble prices: {e}")
            return []
    
    async def scrape_book_summary(self, book_title: str, author: str = None) -> Optional[str]:
        """
        Scrape book summary from Wikipedia.
        
        Args:
            book_title: Book title
            author: Book author (optional)
            
        Returns:
            Book summary string or None
        """
        try:
            # Construct search URL
            search_query = f"{book_title}"
            if author:
                search_query += f" {author}"
            
            search_url = f"https://en.wikipedia.org/wiki/{quote(book_title.replace(' ', '_'))}"
            
            # Get Wikipedia page
            response = await self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the first paragraph of the article
            content_div = soup.find('div', class_='mw-parser-output')
            if content_div:
                paragraphs = content_div.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 100:  # Skip short paragraphs
                        return text[:500] + "..." if len(text) > 500 else text
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Wikipedia summary: {e}")
            return None
    
    async def scrape_all_book_info(self, book_title: str, author: str = None) -> Dict[str, Any]:
        """
        Scrape all available book information from multiple sources.
        
        Args:
            book_title: Book title
            author: Book author (optional)
            
        Returns:
            Dictionary containing all scraped information
        """
        try:
            # Run all scraping tasks concurrently
            tasks = [
                self.scrape_goodreads_reviews(book_title, author, 5),
                self.scrape_amazon_prices(book_title, author),
                self.scrape_barnes_noble_prices(book_title, author),
                self.scrape_book_summary(book_title, author)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            reviews, amazon_prices, bn_prices, summary = results
            
            # Handle exceptions
            if isinstance(reviews, Exception):
                reviews = []
            if isinstance(amazon_prices, Exception):
                amazon_prices = []
            if isinstance(bn_prices, Exception):
                bn_prices = []
            if isinstance(summary, Exception):
                summary = None
            
            return {
                'reviews': reviews,
                'amazon_prices': amazon_prices,
                'barnes_noble_prices': bn_prices,
                'summary': summary,
                'total_reviews': len(reviews),
                'total_price_listings': len(amazon_prices) + len(bn_prices)
            }
            
        except Exception as e:
            logger.error(f"Error scraping all book info: {e}")
            return {
                'reviews': [],
                'amazon_prices': [],
                'barnes_noble_prices': [],
                'summary': None,
                'total_reviews': 0,
                'total_price_listings': 0
            }

# Convenience functions
async def scrape_book_reviews(book_title: str, author: str = None, max_reviews: int = 10) -> List[BookReview]:
    """Scrape book reviews from Goodreads."""
    async with BookWebScraper() as scraper:
        return await scraper.scrape_goodreads_reviews(book_title, author, max_reviews)

async def scrape_book_prices(book_title: str, author: str = None) -> List[BookstoreInfo]:
    """Scrape book prices from multiple stores."""
    async with BookWebScraper() as scraper:
        amazon_prices = await scraper.scrape_amazon_prices(book_title, author)
        bn_prices = await scraper.scrape_barnes_noble_prices(book_title, author)
        return amazon_prices + bn_prices

async def scrape_book_summary(book_title: str, author: str = None) -> Optional[str]:
    """Scrape book summary from Wikipedia."""
    async with BookWebScraper() as scraper:
        return await scraper.scrape_book_summary(book_title, author)

async def scrape_all_book_info(book_title: str, author: str = None) -> Dict[str, Any]:
    """Scrape all available book information."""
    async with BookWebScraper() as scraper:
        return await scraper.scrape_all_book_info(book_title, author)

