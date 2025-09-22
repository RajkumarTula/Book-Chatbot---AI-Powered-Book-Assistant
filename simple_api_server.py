"""
Simplified FastAPI server for the book chatbot.
This version works without Redis and complex dependencies for quick testing.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Book Chatbot API",
    description="A simplified book recommendation and information API",
    version="1.0.0"
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

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    intent: Optional[str] = None

class BookSearchRequest(BaseModel):
    query: str
    max_results: int = 10

class BookSearchResponse(BaseModel):
    books: List[Dict[str, Any]]
    total_results: int
    query: str

# Mock book data for testing
MOCK_BOOKS = [
    {
        "title": "Harry Potter and the Philosopher's Stone",
        "authors": ["J.K. Rowling"],
        "publisher": "Bloomsbury",
        "published_date": "1997-06-26",
        "description": "The first book in the Harry Potter series, following the adventures of a young wizard.",
        "isbn_10": "0747532699",
        "isbn_13": "9780747532699",
        "page_count": 223,
        "categories": ["Fantasy", "Young Adult"],
        "average_rating": 4.5,
        "ratings_count": 1000000,
        "price": 12.99,
        "currency": "USD",
        "availability": "available",
        "thumbnail_url": "https://books.google.com/books/content?id=1Sg40wEACAAJ&printsec=frontcover&img=1&zoom=1",
        "preview_url": "https://books.google.com/books?id=1Sg40wEACAAJ&printsec=frontcover",
        "language": "en"
    },
    {
        "title": "The Great Gatsby",
        "authors": ["F. Scott Fitzgerald"],
        "publisher": "Scribner",
        "published_date": "1925-04-10",
        "description": "A classic American novel set in the Jazz Age, exploring themes of wealth, love, and the American Dream.",
        "isbn_10": "0743273567",
        "isbn_13": "9780743273565",
        "page_count": 180,
        "categories": ["Fiction", "Classic Literature"],
        "average_rating": 4.2,
        "ratings_count": 500000,
        "price": 9.99,
        "currency": "USD",
        "availability": "available",
        "thumbnail_url": "https://books.google.com/books/content?id=1Sg40wEACAAJ&printsec=frontcover&img=1&zoom=1",
        "preview_url": "https://books.google.com/books?id=1Sg40wEACAAJ&printsec=frontcover",
        "language": "en"
    },
    {
        "title": "1984",
        "authors": ["George Orwell"],
        "publisher": "Secker & Warburg",
        "published_date": "1949-06-08",
        "description": "A dystopian social science fiction novel about totalitarian control and surveillance.",
        "isbn_10": "0451524934",
        "isbn_13": "9780451524935",
        "page_count": 328,
        "categories": ["Science Fiction", "Dystopian"],
        "average_rating": 4.7,
        "ratings_count": 800000,
        "price": 11.99,
        "currency": "USD",
        "availability": "available",
        "thumbnail_url": "https://books.google.com/books/content?id=1Sg40wEACAAJ&printsec=frontcover&img=1&zoom=1",
        "preview_url": "https://books.google.com/books?id=1Sg40wEACAAJ&printsec=frontcover",
        "language": "en"
    }
]

def detect_intent(message: str) -> str:
    """Simple intent detection based on keywords."""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["search", "find", "look for", "book"]):
        return "search_book"
    elif any(word in message_lower for word in ["price", "cost", "how much"]):
        return "get_price"
    elif any(word in message_lower for word in ["rating", "review", "stars"]):
        return "get_rating"
    elif any(word in message_lower for word in ["recommend", "suggest", "similar"]):
        return "recommend_books"
    elif any(word in message_lower for word in ["author", "by"]):
        return "search_by_author"
    elif any(word in message_lower for word in ["genre", "category", "type"]):
        return "search_by_genre"
    else:
        return "general"

def search_books(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search for books using mock data."""
    query_lower = query.lower()
    results = []
    
    for book in MOCK_BOOKS:
        if (query_lower in book["title"].lower() or 
            any(query_lower in author.lower() for author in book["authors"]) or
            any(query_lower in category.lower() for category in book["categories"])):
            results.append(book)
    
    return results[:max_results]

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
        "message": "Book Chatbot API is running!"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Main chat endpoint for interacting with the book chatbot."""
    try:
        session_id = message.session_id or f"session_{datetime.now().timestamp()}"
        intent = detect_intent(message.message)
        
        # Process the message based on intent
        if intent == "search_book":
            books = search_books(message.message, 5)
            if books:
                response_text = f"I found {len(books)} books for '{message.message}':\n\n"
                for i, book in enumerate(books, 1):
                    response_text += f"{i}. **{book['title']}**\n"
                    response_text += f"   Authors: {', '.join(book['authors'])}\n"
                    response_text += f"   Published: {book['published_date']}\n"
                    response_text += f"   Rating: {book['average_rating']}/5 ({book['ratings_count']} ratings)\n"
                    response_text += f"   Price: ${book['price']} {book['currency']}\n\n"
            else:
                response_text = f"I couldn't find any books matching '{message.message}'. Try searching for popular books like 'Harry Potter', 'The Great Gatsby', or '1984'."
        
        elif intent == "get_price":
            books = search_books(message.message, 1)
            if books:
                book = books[0]
                response_text = f"**Price Information for '{book['title']}'**\n\n"
                response_text += f"**Price:** ${book['price']} {book['currency']}\n"
                response_text += f"**Availability:** {book['availability']}\n"
            else:
                response_text = f"I couldn't find price information for '{message.message}'. Try searching for a specific book title."
        
        elif intent == "get_rating":
            books = search_books(message.message, 1)
            if books:
                book = books[0]
                response_text = f"**Rating Information for '{book['title']}'**\n\n"
                response_text += f"**Average Rating:** {book['average_rating']}/5 stars\n"
                response_text += f"**Number of Ratings:** {book['ratings_count']:,}\n"
            else:
                response_text = f"I couldn't find rating information for '{message.message}'. Try searching for a specific book title."
        
        elif intent == "recommend_books":
            books = search_books("popular", 5)
            response_text = f"**Book Recommendations:**\n\n"
            for i, book in enumerate(books, 1):
                response_text += f"{i}. **{book['title']}**\n"
                response_text += f"   Authors: {', '.join(book['authors'])}\n"
                response_text += f"   Published: {book['published_date']}\n"
                response_text += f"   Rating: {book['average_rating']}/5\n\n"
        
        else:
            response_text = "Hello! I'm your personal book assistant. I can help you find books, get recommendations, check prices, and ratings. Try asking me about books like 'Harry Potter', 'The Great Gatsby', or '1984'."
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now(),
            intent=intent
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/search", response_model=BookSearchResponse)
async def search_books_endpoint(request: BookSearchRequest):
    """Search for books."""
    try:
        books = search_books(request.query, request.max_results)
        
        return BookSearchResponse(
            books=books,
            total_results=len(books),
            query=request.query
        )
    
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/books")
async def get_all_books():
    """Get all available books."""
    return {
        "books": MOCK_BOOKS,
        "total_results": len(MOCK_BOOKS)
    }

if __name__ == "__main__":
    print("🚀 Starting Book Chatbot API Server...")
    print("=" * 50)
    print("📚 Book Chatbot API")
    print("🌐 Server: http://localhost:8000")
    print("📖 Web Interface: http://localhost:8000")
    print("🔍 API Documentation: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "simple_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
