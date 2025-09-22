"""
LangChain RAG implementation for enhanced book recommendations and responses.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from .google_books_api import BookInfo, search_books, get_book_by_title

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BookRecommendation:
    """Data class for book recommendations."""
    book: BookInfo
    similarity_score: float
    reason: str

class BookRAGSystem:
    """Retrieval-Augmented Generation system for book recommendations."""
    
    def __init__(self, openai_api_key: str = None, persist_directory: str = "./chroma_db"):
        """
        Initialize the RAG system.
        
        Args:
            openai_api_key: OpenAI API key for LLM
            persist_directory: Directory to persist vector database
        """
        self.openai_api_key = openai_api_key
        self.persist_directory = persist_directory
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize vector store
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Book knowledge base
        self.book_knowledge = []
        
    async def initialize(self):
        """Initialize the RAG system components."""
        try:
            # Initialize vector store
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            # Initialize retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            # Initialize QA chain if OpenAI key is provided
            if self.openai_api_key:
                llm = OpenAI(
                    openai_api_key=self.openai_api_key,
                    temperature=0.7,
                    max_tokens=500
                )
                
                # Create custom prompt
                prompt_template = """
                You are a knowledgeable book assistant. Use the following context to answer questions about books.
                If you don't know the answer based on the context, say so.
                
                Context: {context}
                
                Question: {question}
                
                Answer: Provide a helpful and accurate response about books based on the context.
                """
                
                PROMPT = PromptTemplate(
                    template=prompt_template,
                    input_variables=["context", "question"]
                )
                
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=self.retriever,
                    memory=self.memory,
                    prompt=PROMPT,
                    return_source_documents=True
                )
            
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            raise
    
    def _create_book_document(self, book: BookInfo) -> Document:
        """Create a LangChain Document from BookInfo."""
        content = f"""
        Title: {book.title}
        Authors: {', '.join(book.authors)}
        Publisher: {book.publisher}
        Published Date: {book.published_date}
        Description: {book.description}
        Categories: {', '.join(book.categories) if book.categories else 'N/A'}
        Average Rating: {book.average_rating or 'N/A'}
        Ratings Count: {book.ratings_count or 'N/A'}
        Page Count: {book.page_count or 'N/A'}
        Language: {book.language}
        ISBN-10: {book.isbn_10 or 'N/A'}
        ISBN-13: {book.isbn_13 or 'N/A'}
        Price: {f'${book.price} {book.currency}' if book.price else 'N/A'}
        Availability: {book.availability}
        """
        
        metadata = {
            "title": book.title,
            "authors": book.authors,
            "publisher": book.publisher,
            "published_date": book.published_date,
            "categories": book.categories,
            "average_rating": book.average_rating,
            "ratings_count": book.ratings_count,
            "page_count": book.page_count,
            "language": book.language,
            "isbn_10": book.isbn_10,
            "isbn_13": book.isbn_13,
            "price": book.price,
            "currency": book.currency,
            "availability": book.availability
        }
        
        return Document(page_content=content, metadata=metadata)
    
    async def add_books_to_knowledge_base(self, books: List[BookInfo]):
        """Add books to the knowledge base."""
        try:
            documents = []
            for book in books:
                doc = self._create_book_document(book)
                documents.append(doc)
            
            # Split documents
            split_docs = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            if self.vectorstore:
                self.vectorstore.add_documents(split_docs)
                self.vectorstore.persist()
            
            # Store in memory for quick access
            self.book_knowledge.extend(books)
            
            logger.info(f"Added {len(books)} books to knowledge base")
            
        except Exception as e:
            logger.error(f"Error adding books to knowledge base: {e}")
    
    async def search_similar_books(self, query: str, max_results: int = 5) -> List[BookRecommendation]:
        """
        Find similar books using vector similarity search.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of BookRecommendation objects
        """
        try:
            if not self.vectorstore:
                return []
            
            # Perform similarity search
            docs = self.vectorstore.similarity_search_with_score(query, k=max_results)
            
            recommendations = []
            for doc, score in docs:
                # Find the original book info
                book_info = self._find_book_by_title(doc.metadata.get('title', ''))
                if book_info:
                    recommendation = BookRecommendation(
                        book=book_info,
                        similarity_score=1 - score,  # Convert distance to similarity
                        reason=f"Similar content and themes to '{query}'"
                    )
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error searching similar books: {e}")
            return []
    
    def _find_book_by_title(self, title: str) -> Optional[BookInfo]:
        """Find book by title in the knowledge base."""
        for book in self.book_knowledge:
            if book.title.lower() == title.lower():
                return book
        return None
    
    async def get_enhanced_recommendations(self, user_query: str, max_results: int = 5) -> List[BookRecommendation]:
        """
        Get enhanced book recommendations using RAG.
        
        Args:
            user_query: User's query
            max_results: Maximum number of results
            
        Returns:
            List of BookRecommendation objects
        """
        try:
            # First, search for books using Google Books API
            search_results = await search_books(user_query, max_results * 2)
            
            if not search_results:
                return []
            
            # Add to knowledge base if not already present
            new_books = []
            for book in search_results:
                if not self._find_book_by_title(book.title):
                    new_books.append(book)
            
            if new_books:
                await self.add_books_to_knowledge_base(new_books)
            
            # Get similar books using vector search
            similar_books = await self.search_similar_books(user_query, max_results)
            
            # Combine and rank results
            all_recommendations = []
            
            # Add search results
            for book in search_results[:max_results]:
                recommendation = BookRecommendation(
                    book=book,
                    similarity_score=1.0,  # Direct match
                    reason=f"Direct match for '{user_query}'"
                )
                all_recommendations.append(recommendation)
            
            # Add similar books (avoid duplicates)
            existing_titles = {rec.book.title.lower() for rec in all_recommendations}
            for rec in similar_books:
                if rec.book.title.lower() not in existing_titles:
                    all_recommendations.append(rec)
            
            # Sort by similarity score
            all_recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
            
            return all_recommendations[:max_results]
            
        except Exception as e:
            logger.error(f"Error getting enhanced recommendations: {e}")
            return []
    
    async def answer_question(self, question: str) -> str:
        """
        Answer a question using the RAG system.
        
        Args:
            question: User's question
            
        Returns:
            Answer string
        """
        try:
            if not self.qa_chain:
                return "I'm sorry, the AI language model is not available. Please check your OpenAI API key."
            
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            return result["result"]
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I'm sorry, I encountered an error while processing your question."
    
    async def get_book_comparison(self, book1_title: str, book2_title: str) -> str:
        """
        Compare two books using RAG.
        
        Args:
            book1_title: First book title
            book2_title: Second book title
            
        Returns:
            Comparison string
        """
        try:
            # Get book information
            book1 = await get_book_by_title(book1_title)
            book2 = await get_book_by_title(book2_title)
            
            if not book1 or not book2:
                return "I couldn't find one or both of the books you mentioned."
            
            # Add books to knowledge base if not present
            books_to_add = []
            if not self._find_book_by_title(book1.title):
                books_to_add.append(book1)
            if not self._find_book_by_title(book2.title):
                books_to_add.append(book2)
            
            if books_to_add:
                await self.add_books_to_knowledge_base(books_to_add)
            
            # Create comparison
            comparison = f"""
            **{book1.title}** vs **{book2.title}**
            
            **{book1.title}:**
            - Authors: {', '.join(book1.authors)}
            - Published: {book1.published_date}
            - Rating: {book1.average_rating or 'N/A'} ({book1.ratings_count or 0} ratings)
            - Pages: {book1.page_count or 'N/A'}
            - Price: {f'${book1.price} {book1.currency}' if book1.price else 'N/A'}
            - Description: {book1.description[:200]}...
            
            **{book2.title}:**
            - Authors: {', '.join(book2.authors)}
            - Published: {book2.published_date}
            - Rating: {book2.average_rating or 'N/A'} ({book2.ratings_count or 0} ratings)
            - Pages: {book2.page_count or 'N/A'}
            - Price: {f'${book2.price} {book2.currency}' if book2.price else 'N/A'}
            - Description: {book2.description[:200]}...
            """
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing books: {e}")
            return "I'm sorry, I encountered an error while comparing the books."
    
    async def get_genre_recommendations(self, genre: str, max_results: int = 5) -> List[BookRecommendation]:
        """
        Get book recommendations for a specific genre.
        
        Args:
            genre: Genre name
            max_results: Maximum number of results
            
        Returns:
            List of BookRecommendation objects
        """
        try:
            # Search for books in the genre
            books = await search_books(f"subject:{genre}", max_results * 2)
            
            if not books:
                return []
            
            # Add to knowledge base
            await self.add_books_to_knowledge_base(books)
            
            # Create recommendations
            recommendations = []
            for book in books[:max_results]:
                recommendation = BookRecommendation(
                    book=book,
                    similarity_score=1.0,
                    reason=f"Popular {genre} book"
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting genre recommendations: {e}")
            return []

# Global instance
rag_system = BookRAGSystem()

# Convenience functions
async def initialize_rag_system(openai_api_key: str = None):
    """Initialize the RAG system."""
    global rag_system
    rag_system = BookRAGSystem(openai_api_key)
    await rag_system.initialize()

async def get_enhanced_recommendations(query: str, max_results: int = 5) -> List[BookRecommendation]:
    """Get enhanced book recommendations."""
    return await rag_system.get_enhanced_recommendations(query, max_results)

async def answer_question(question: str) -> str:
    """Answer a question using RAG."""
    return await rag_system.answer_question(question)

async def get_book_comparison(book1_title: str, book2_title: str) -> str:
    """Compare two books."""
    return await rag_system.get_book_comparison(book1_title, book2_title)

async def get_genre_recommendations(genre: str, max_results: int = 5) -> List[BookRecommendation]:
    """Get genre recommendations."""
    return await rag_system.get_genre_recommendations(genre, max_results)

