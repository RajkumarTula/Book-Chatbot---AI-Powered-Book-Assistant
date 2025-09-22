"""
Enhanced Book Chatbot API Server with Google Books API and Dataset Integration.
This version uses both the local dataset and Google Books API for comprehensive book information.
"""

import asyncio
import logging
import pandas as pd
import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from difflib import SequenceMatcher

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env if present
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Book Chatbot API",
    description="A comprehensive book recommendation and information API with Google Books integration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="web"), name="static")

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    source_preference: Optional[str] = "ask"  # "dataset" | "google" | "both" | "ask"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    intent: Optional[str] = None
    source: Optional[str] = None  # "dataset" or "google_books"

class BookSearchRequest(BaseModel):
    query: str
    max_results: int = 10
    # source: dataset | google | both
    source: str = "both"

class BookSearchResponse(BaseModel):
    books: List[Dict[str, Any]]
    total_results: int
    query: str
    source: str

# Load the dataset
def load_dataset():
    """Load the book dataset from CSV file."""
    try:
        df = pd.read_csv('Booky/data/data.csv')
        logger.info(f"Loaded dataset with {len(df)} books")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return pd.DataFrame()

# Load env and dataset on startup
load_dotenv()
BOOK_DATASET = load_dataset()

# Google Books API configuration
GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY', '')
GOOGLE_BOOKS_BASE_URL = 'https://www.googleapis.com/books/v1/volumes'

def similarity(a, b):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def search_dataset(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search the local dataset for books."""
    if BOOK_DATASET.empty:
        return []
    
    query_lower = query.lower()
    results = []
    
    # Search in title, authors, and categories
    for _, row in BOOK_DATASET.iterrows():
        score = 0
        book_data = {
            'title': str(row['title']),
            'authors': str(row['authors']).split(';') if pd.notna(row['authors']) else [],
            'categories': str(row['categories']).split(';') if pd.notna(row['categories']) else [],
            'description': str(row['description']) if pd.notna(row['description']) else '',
            'published_year': int(row['published_year']) if pd.notna(row['published_year']) else None,
            'average_rating': float(row['average_rating']) if pd.notna(row['average_rating']) else None,
            'num_pages': int(row['num_pages']) if pd.notna(row['num_pages']) else None,
            'ratings_count': int(row['ratings_count']) if pd.notna(row['ratings_count']) else 0,
            'thumbnail': str(row['thumbnail']) if pd.notna(row['thumbnail']) else '',
            'isbn13': str(row['isbn13']) if pd.notna(row['isbn13']) else '',
            'isbn10': str(row['isbn10']) if pd.notna(row['isbn10']) else '',
            'source': 'dataset'
        }
        
        # Calculate relevance score
        if query_lower in book_data['title'].lower():
            score += 10
        if any(query_lower in author.lower() for author in book_data['authors']):
            score += 8
        if any(query_lower in cat.lower() for cat in book_data['categories']):
            score += 6
        if query_lower in book_data['description'].lower():
            score += 4
        
        # Add similarity bonus
        title_sim = similarity(query, book_data['title'])
        score += title_sim * 5
        
        if score > 0:
            book_data['relevance_score'] = score
            results.append(book_data)
    
    # Sort by relevance score and return top results
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:max_results]

async def search_google_books(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Google Books API for books."""
    if not GOOGLE_BOOKS_API_KEY:
        logger.warning("Google Books API key not found, skipping Google Books search")
        return []
    
    try:
        params = {
            'q': query,
            'key': GOOGLE_BOOKS_API_KEY,
            'maxResults': max_results
        }
        
        response = requests.get(GOOGLE_BOOKS_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        books = []
        for item in data.get('items', []):
            volume_info = item.get('volumeInfo', {})
            book_data = {
                'title': volume_info.get('title', ''),
                'authors': volume_info.get('authors', []),
                'categories': volume_info.get('categories', []),
                'description': volume_info.get('description', ''),
                'published_year': volume_info.get('publishedDate', '').split('-')[0] if volume_info.get('publishedDate') else None,
                'average_rating': volume_info.get('averageRating'),
                'num_pages': volume_info.get('pageCount'),
                'ratings_count': volume_info.get('ratingsCount', 0),
                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                'isbn13': '',
                'isbn10': '',
                'source': 'google_books',
                'google_id': item.get('id', ''),
                'preview_url': volume_info.get('previewLink', ''),
                'info_url': volume_info.get('infoLink', '')
            }
            
            # Extract ISBNs
            for identifier in volume_info.get('industryIdentifiers', []):
                if identifier.get('type') == 'ISBN_13':
                    book_data['isbn13'] = identifier.get('identifier', '')
                elif identifier.get('type') == 'ISBN_10':
                    book_data['isbn10'] = identifier.get('identifier', '')
            
            books.append(book_data)
        
        return books
        
    except Exception as e:
        logger.error(f"Error searching Google Books API: {e}")
        return []

def detect_intent(message: str) -> str:
    """Enhanced intent detection based on keywords."""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["search", "find", "look for", "book"]):
        return "search_book"
    elif any(word in message_lower for word in ["price", "cost", "how much", "buy"]):
        return "get_price"
    elif any(word in message_lower for word in ["rating", "review", "stars", "score"]):
        return "get_rating"
    elif any(word in message_lower for word in ["recommend", "suggest", "similar", "like"]):
        return "recommend_books"
    elif any(word in message_lower for word in ["author", "by", "written by"]):
        return "search_by_author"
    elif any(word in message_lower for word in ["genre", "category", "type", "kind"]):
        return "search_by_genre"
    elif any(word in message_lower for word in ["year", "published", "release", "new", "new releases", "latest"]):
        return "new_releases"
    elif any(word in message_lower for word in ["pages", "length", "thick", "short"]):
        return "search_by_pages"
    elif any(word in message_lower for word in ["bestseller", "trending", "popular", "top charts"]):
        return "bestsellers"
    elif any(word in message_lower for word in ["compare", "vs", "difference between"]):
        return "compare_books"
    else:
        return "general"

def format_book_info(book: Dict[str, Any], detailed: bool = False) -> str:
    """Format book information for display."""
    info = f"**{book['title']}**"
    
    if book['authors']:
        authors = ', '.join(book['authors']) if isinstance(book['authors'], list) else book['authors']
        info += f"\n👤 **Authors:** {authors}"
    
    if book['published_year']:
        info += f"\n📅 **Published:** {book['published_year']}"
    
    if book['average_rating']:
        info += f"\n⭐ **Rating:** {book['average_rating']}/5"
        if book['ratings_count']:
            info += f" ({book['ratings_count']:,} ratings)"
    
    if book['num_pages']:
        info += f"\n📖 **Pages:** {book['num_pages']}"
    
    if book['categories']:
        categories = ', '.join(book['categories']) if isinstance(book['categories'], list) else book['categories']
        info += f"\n🏷️ **Categories:** {categories}"
    
    if detailed and book['description']:
        desc = book['description'][:200] + "..." if len(book['description']) > 200 else book['description']
        info += f"\n📝 **Description:** {desc}"
    
    info += f"\n🔍 **Source:** {book['source'].title()}"
    
    return info

@app.get("/")
async def root():
    """Root endpoint - serve the web interface."""
    return FileResponse("web/index.html")

@app.get("/styles.css")
async def get_css():
    """Serve CSS file."""
    return FileResponse("web/styles.css")

@app.get("/script.js")
async def get_js():
    """Serve JavaScript file."""
    return FileResponse("web/script.js")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "message": "Enhanced Book Chatbot API is running!",
        "dataset_loaded": not BOOK_DATASET.empty,
        "google_books_available": bool(GOOGLE_BOOKS_API_KEY),
        "total_books": len(BOOK_DATASET) if not BOOK_DATASET.empty else 0
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Chat endpoint that proxies to Rasa server."""
    try:
        # Forward the request to Rasa server
        rasa_url = "http://localhost:5005/webhooks/rest/webhook"
        rasa_payload = {
            "sender": message.session_id or f"session_{datetime.now().timestamp()}",
            "message": message.message
        }

        response = requests.post(rasa_url, json=rasa_payload, timeout=30)
        response.raise_for_status()

        rasa_response = response.json()

        # Extract the bot response
        bot_messages = [msg for msg in rasa_response if msg.get("recipient_id") == rasa_payload["sender"]]
        bot_text = "\n".join(msg.get("text", "") for msg in bot_messages) if bot_messages else "Sorry, I couldn't process your request."

        return ChatResponse(
            response=bot_text,
            session_id=message.session_id or rasa_payload["sender"],
            timestamp=datetime.now(),
            intent=None,  # Rasa doesn't return intent in webhook response
            source="rasa"
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Rasa server: {e}")
        # Fallback to local processing if Rasa is not available
        session_id = message.session_id or f"session_{datetime.now().timestamp()}"
        intent = detect_intent(message.message)
        # resolve source preference
        source_pref = (message.source_preference or "ask").lower()
        if source_pref not in {"dataset", "google", "both", "ask"}:
            source_pref = "ask"

        # Process the message based on intent
        if intent == "search_book":
            # Determine sources
            use_dataset = source_pref in {"dataset", "both"}
            use_google = source_pref in {"google", "both"}
            if source_pref == "ask":
                prompt = (
                    "I can search the local dataset or the Internet (Google Books).\n\n"
                    "Please reply with one of: 'dataset', 'internet', or 'both'."
                )
                return ChatResponse(
                    response=prompt,
                    session_id=session_id,
                    timestamp=datetime.now(),
                    intent=intent,
                    source="prompt"
                )

            dataset_results = search_dataset(message.message, 5) if use_dataset else []
            google_results = await search_google_books(message.message, 5) if use_google else []
            
            # Combine and deduplicate results
            all_results = dataset_results + google_results
            unique_results = []
            seen_titles = set()
            
            for book in all_results:
                title_key = book['title'].lower().strip()
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    unique_results.append(book)
            
            if unique_results:
                response_text = f"🔍 **Found {len(unique_results)} books for '{message.message}':**\n\n"
                for i, book in enumerate(unique_results[:5], 1):
                    response_text += f"{i}. {format_book_info(book)}\n\n"
            else:
                response_text = f"❌ I couldn't find any books matching '{message.message}'. Try searching for popular books or authors."
        
        elif intent == "get_price":
            # Search for price information
            dataset_results = search_dataset(message.message, 1)
            if dataset_results:
                book = dataset_results[0]
                response_text = f"💰 **Price Information for '{book['title']}'**\n\n"
                response_text += f"📖 **Book:** {book['title']}\n"
                response_text += f"👤 **Author:** {', '.join(book['authors']) if book['authors'] else 'Unknown'}\n"
                response_text += f"⭐ **Rating:** {book['average_rating']}/5" if book['average_rating'] else "No rating available"
                response_text += f"\n🔍 **Source:** {book['source'].title()}\n\n"
                response_text += "💡 *Note: For current pricing, please check online retailers or bookstores.*"
            else:
                response_text = f"❌ I couldn't find price information for '{message.message}'. Try searching for a specific book title."
        
        elif intent == "get_rating":
            dataset_results = search_dataset(message.message, 1)
            if dataset_results:
                book = dataset_results[0]
                response_text = f"⭐ **Rating Information for '{book['title']}'**\n\n"
                response_text += f"📖 **Book:** {book['title']}\n"
                response_text += f"👤 **Author:** {', '.join(book['authors']) if book['authors'] else 'Unknown'}\n"
                if book['average_rating']:
                    response_text += f"⭐ **Average Rating:** {book['average_rating']}/5 stars\n"
                    if book['ratings_count']:
                        response_text += f"📊 **Number of Ratings:** {book['ratings_count']:,}\n"
                else:
                    response_text += "⭐ **Rating:** No rating available\n"
                response_text += f"🔍 **Source:** {book['source'].title()}"
            else:
                response_text = f"❌ I couldn't find rating information for '{message.message}'. Try searching for a specific book title."
        
        elif intent == "recommend_books":
            # Get recommendations from dataset
            popular_books = BOOK_DATASET.nlargest(5, 'average_rating') if not BOOK_DATASET.empty else []
            response_text = f"📚 **Book Recommendations:**\n\n"
            
            if not popular_books.empty:
                for i, (_, book) in enumerate(popular_books.iterrows(), 1):
                    response_text += f"{i}. **{book['title']}**\n"
                    response_text += f"   👤 **Author:** {book['authors']}\n"
                    response_text += f"   ⭐ **Rating:** {book['average_rating']}/5\n"
                    response_text += f"   📅 **Year:** {book['published_year']}\n\n"
            else:
                response_text += "🌟 **Top Recommendations:**\n\n"
                response_text += "1. **Harry Potter and the Philosopher's Stone** by J.K. Rowling\n"
                response_text += "2. **The Great Gatsby** by F. Scott Fitzgerald\n"
                response_text += "3. **1984** by George Orwell\n"
                response_text += "4. **To Kill a Mockingbird** by Harper Lee\n"
                response_text += "5. **Pride and Prejudice** by Jane Austen\n\n"
                response_text += "💡 *These are popular classics that are highly recommended!*"
        
        elif intent == "search_by_author":
            author_query = message.message.lower()
            # Extract author name from query
            author_keywords = ["by", "author", "written by"]
            for keyword in author_keywords:
                if keyword in author_query:
                    author_query = author_query.split(keyword)[-1].strip()
                    break
            
            use_dataset = source_pref in {"dataset", "both"}
            use_google = source_pref in {"google", "both"}

            dataset_results = search_dataset(author_query, 5) if use_dataset else []
            google_results = await search_google_books(f'inauthor:"{author_query}"', 5) if use_google else []
            all_results = dataset_results + google_results
            if dataset_results:
                response_text = f"👤 **Books by '{author_query.title()}':**\n\n"
                for i, book in enumerate(all_results[:5], 1):
                    response_text += f"{i}. {format_book_info(book)}\n\n"
            else:
                response_text = f"❌ I couldn't find books by '{author_query.title()}'. Try searching for a different author."
        
        elif intent == "search_by_genre":
            genre_query = message.message.lower()
            use_dataset = source_pref in {"dataset", "both"}
            use_google = source_pref in {"google", "both"}
            dataset_results = search_dataset(genre_query, 5) if use_dataset else []
            google_results = await search_google_books(f'subject:"{genre_query}"', 5) if use_google else []
            all_results = dataset_results + google_results
            if all_results:
                response_text = f"🏷️ **{genre_query.title()} Books:**\n\n"
                for i, book in enumerate(all_results[:5], 1):
                    response_text += f"{i}. {format_book_info(book)}\n\n"
            else:
                response_text = f"❌ I couldn't find {genre_query.title()} books. Try searching for a different genre."

        elif intent == "bestsellers":
            use_dataset = source_pref in {"dataset", "both"}
            use_google = source_pref in {"google", "both"}
            dataset_results = search_dataset("bestseller", 5) if use_dataset else []
            google_results = await search_google_books("bestseller OR popular OR trending", 5) if use_google else []
            all_results = dataset_results + google_results
            if all_results:
                response_text = f"🌟 **Bestsellers & Trending Books:**\n\n"
                for i, book in enumerate(all_results[:5], 1):
                    response_text += f"{i}. {format_book_info(book)}\n\n"
            else:
                response_text = "❌ I couldn't find bestsellers at the moment."

        elif intent == "new_releases":
            use_dataset = source_pref in {"dataset", "both"}
            use_google = source_pref in {"google", "both"}
            # Dataset fallback: recent years keyword
            dataset_results = search_dataset("2023", 3) + search_dataset("2024", 3) if use_dataset else []
            google_results = await search_google_books("publishedDate:>2023", 6) if use_google else []
            all_results = dataset_results + google_results
            if all_results:
                response_text = f"🆕 **New Releases:**\n\n"
                for i, book in enumerate(all_results[:6], 1):
                    response_text += f"{i}. {format_book_info(book)}\n\n"
            else:
                response_text = "❌ I couldn't find new releases right now."

        elif intent == "compare_books":
            # Very simple compare: split on ' vs ' if present
            parts = [p.strip() for p in message.message.lower().split(" vs ")]
            titles = parts if len(parts) == 2 else []
            if len(titles) == 2:
                left = (search_dataset(titles[0], 1) or (await search_google_books(titles[0], 1)))
                right = (search_dataset(titles[1], 1) or (await search_google_books(titles[1], 1)))
                if left and right:
                    l = left[0]
                    r = right[0]
                    response_text = (
                        f"📊 **Comparison**\n\n"
                        f"• {l['title']} — ⭐ {l.get('average_rating','-')}/5, 📖 {l.get('num_pages','-')} pages, 🏷️ {', '.join(l.get('categories', [])) if l.get('categories') else '-'} (Source: {l['source'].title()})\n"
                        f"• {r['title']} — ⭐ {r.get('average_rating','-')}/5, 📖 {r.get('num_pages','-')} pages, 🏷️ {', '.join(r.get('categories', [])) if r.get('categories') else '-'} (Source: {r['source'].title()})\n"
                    )
                else:
                    response_text = "❌ I couldn't fetch both books to compare. Try exact titles like 'The Hobbit vs The Lord of the Rings'."
            else:
                response_text = "Please specify two titles like 'Book A vs Book B'."
        
        else:
            response_text = "👋 **Hello! I'm your enhanced book assistant!**\n\n"
            response_text += "I can help you with:\n"
            response_text += "🔍 **Search books** - Find books by title, author, or genre\n"
            response_text += "⭐ **Check ratings** - Get book ratings and reviews\n"
            response_text += "💰 **Price information** - Get book pricing details\n"
            response_text += "📚 **Recommendations** - Get personalized book suggestions\n"
            response_text += "👤 **Author search** - Find books by specific authors\n"
            response_text += "🏷️ **Genre search** - Discover books by category\n\n"
            response_text += "🌐 **Data source** - I can use the local dataset or the Internet (Google Books).\n"
            response_text += "Type 'dataset', 'internet', or 'both' anytime to switch.\n\n"
            response_text += "**Try asking:**\n"
            response_text += "• \"Find books by Stephen King\"\n"
            response_text += "• \"Show me fantasy books\"\n"
            response_text += "• \"What's the rating of Harry Potter?\"\n"
            response_text += "• \"Recommend some good books\""
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now(),
            intent=intent,
            source="hybrid"
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/search", response_model=BookSearchResponse)
async def search_books_endpoint(request: BookSearchRequest):
    """Enhanced search endpoint with both dataset and Google Books."""
    try:
        use_dataset = request.source in {"dataset", "both"}
        use_google = request.source in {"google", "both"}
        dataset_results = search_dataset(request.query, request.max_results) if use_dataset else []
        google_results = await search_google_books(request.query, request.max_results) if use_google else []
        # Combine results
        all_results = dataset_results + google_results
        source = request.source
        
        return BookSearchResponse(
            books=all_results,
            total_results=len(all_results),
            query=request.query,
            source=source
        )
    
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/books")
async def get_all_books():
    """Get all available books from dataset."""
    if BOOK_DATASET.empty:
        return {"books": [], "total_results": 0, "message": "Dataset not loaded"}
    
    books = []
    for _, row in BOOK_DATASET.head(100).iterrows():  # Limit to first 100 for performance
        book_data = {
            'title': str(row['title']),
            'authors': str(row['authors']).split(';') if pd.notna(row['authors']) else [],
            'categories': str(row['categories']).split(';') if pd.notna(row['categories']) else [],
            'published_year': int(row['published_year']) if pd.notna(row['published_year']) else None,
            'average_rating': float(row['average_rating']) if pd.notna(row['average_rating']) else None,
            'source': 'dataset'
        }
        books.append(book_data)
    
    return {
        "books": books,
        "total_results": len(books),
        "total_in_dataset": len(BOOK_DATASET)
    }

@app.get("/stats")
async def get_stats():
    """Get dataset statistics."""
    if BOOK_DATASET.empty:
        return {"message": "Dataset not loaded"}
    
    stats = {
        "total_books": len(BOOK_DATASET),
        "average_rating": BOOK_DATASET['average_rating'].mean(),
        "total_pages": BOOK_DATASET['num_pages'].sum(),
        "publication_years": {
            "earliest": int(BOOK_DATASET['published_year'].min()),
            "latest": int(BOOK_DATASET['published_year'].max())
        },
        "top_categories": BOOK_DATASET['categories'].value_counts().head(10).to_dict(),
        "top_authors": BOOK_DATASET['authors'].value_counts().head(10).to_dict()
    }
    
    return stats

@app.post("/book-details")
async def book_details(payload: Dict[str, Any]):
    """Return merged book details by title from dataset and Google Books with source attribution."""
    try:
        title = str(payload.get("title", "")).strip()
        if not title:
            raise HTTPException(status_code=400, detail="Missing title")

        dataset_match = search_dataset(title, 1)
        google_match = await search_google_books(f'intitle:"{title}"', 1)

        # Prefer dataset fields, fill gaps from Google
        base = dataset_match[0] if dataset_match else {}
        web = google_match[0] if google_match else {}

        merged = {
            "title": base.get("title") or web.get("title") or title,
            "authors": base.get("authors") or web.get("authors") or [],
            "categories": base.get("categories") or web.get("categories") or [],
            "description": base.get("description") or web.get("description") or "",
            "published_year": base.get("published_year") or web.get("published_year"),
            "average_rating": base.get("average_rating") or web.get("average_rating"),
            "num_pages": base.get("num_pages") or web.get("num_pages"),
            "ratings_count": base.get("ratings_count") or web.get("ratings_count"),
            "thumbnail": base.get("thumbnail") or web.get("thumbnail"),
            "isbn13": base.get("isbn13") or web.get("isbn13"),
            "isbn10": base.get("isbn10") or web.get("isbn10"),
            "preview_url": web.get("preview_url"),
            "info_url": web.get("info_url"),
            "sources": list({s for s in [base.get("source"), web.get("source")] if s}) or (["dataset"] if base else ["google_books"]) 
        }

        return merged
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in book-details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    print("Starting Enhanced Book Chatbot API Server...")
    print("=" * 60)
    print("Enhanced Book Chatbot API")
    print("Server: http://localhost:8000")
    print("Web Interface: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Dataset Status:", "Loaded" if not BOOK_DATASET.empty else "Not loaded")
    print("Google Books API:", "Available" if GOOGLE_BOOKS_API_KEY else "Not configured")
    print("=" * 60)
    
    uvicorn.run(
        "enhanced_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


