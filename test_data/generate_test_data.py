#!/usr/bin/env python3
"""
Generate comprehensive test data for the book chatbot.
This script creates 1000+ book-related queries for testing.
"""

import json
import random
from typing import List, Dict, Any

# Popular book titles for testing
POPULAR_BOOKS = [
    "Harry Potter", "The Great Gatsby", "1984", "To Kill a Mockingbird",
    "The Hobbit", "Dune", "Pride and Prejudice", "The Catcher in the Rye",
    "The Lord of the Rings", "The Hunger Games", "The Handmaid's Tale",
    "The Alchemist", "The Kite Runner", "The Book Thief", "The Fault in Our Stars",
    "Gone with the Wind", "The Chronicles of Narnia", "The Da Vinci Code",
    "The Girl with the Dragon Tattoo", "The Help", "The Lovely Bones",
    "The Time Traveler's Wife", "Water for Elephants", "The Secret",
    "The Seven Husbands of Evelyn Hugo", "Where the Crawdads Sing",
    "The Silent Patient", "The Midnight Library", "Project Hail Mary"
]

# Popular authors for testing
POPULAR_AUTHORS = [
    "Stephen King", "J.K. Rowling", "George Orwell", "Harper Lee",
    "J.R.R. Tolkien", "Frank Herbert", "Jane Austen", "J.D. Salinger",
    "Suzanne Collins", "Margaret Atwood", "Paulo Coelho", "Khaled Hosseini",
    "Markus Zusak", "John Green", "Margaret Mitchell", "C.S. Lewis",
    "Dan Brown", "Stieg Larsson", "Kathryn Stockett", "Alice Sebold",
    "Audrey Niffenegger", "Sara Gruen", "Rhonda Byrne", "Taylor Jenkins Reid",
    "Delia Owens", "Alex Michaelides", "Matt Haig", "Andy Weir"
]

# Book genres for testing
GENRES = [
    "fiction", "mystery", "romance", "science fiction", "fantasy",
    "thriller", "biography", "history", "self-help", "poetry",
    "young adult", "children's", "cooking", "travel", "business",
    "psychology", "art", "photography", "gardening", "health",
    "memoir", "autobiography", "philosophy", "religion", "education"
]

# Price ranges for testing
PRICE_RANGES = [
    "under $10", "under $15", "under $20", "under $25", "under $30",
    "under $5", "under $50", "cheap", "affordable", "budget",
    "expensive", "premium", "luxury", "discount", "sale"
]

# Rating queries
RATING_TERMS = [
    "rating", "stars", "review", "score", "grade", "evaluation",
    "assessment", "opinion", "feedback", "critique", "judgment"
]

# Availability terms
AVAILABILITY_TERMS = [
    "available", "in stock", "out of stock", "sold out", "backorder",
    "pre-order", "coming soon", "discontinued", "limited edition"
]

# Bookstore names
BOOKSTORES = [
    "Amazon", "Barnes & Noble", "Waterstones", "Indigo", "Chapters",
    "Books-A-Million", "Powell's", "Half Price Books", "Book Depository",
    "Target", "Walmart", "Costco", "Sam's Club"
]

def generate_search_queries() -> List[str]:
    """Generate book search queries."""
    queries = []
    
    # Search by title
    for book in POPULAR_BOOKS:
        queries.extend([
            f"Find {book}",
            f"Search for {book}",
            f"Look for {book}",
            f"I want to read {book}",
            f"Show me {book}",
            f"Get me {book}",
            f"Find books about {book}",
            f"Search {book} book"
        ])
    
    # Search by author
    for author in POPULAR_AUTHORS:
        queries.extend([
            f"Books by {author}",
            f"Find {author} books",
            f"Search for {author}",
            f"Show me {author} novels",
            f"Get {author} works",
            f"Look for {author} books",
            f"Find all {author} books",
            f"Search {author} novels"
        ])
    
    # Search by genre
    for genre in GENRES:
        queries.extend([
            f"{genre} books",
            f"Find {genre} novels",
            f"Search for {genre}",
            f"Show me {genre} books",
            f"Get {genre} recommendations",
            f"Look for {genre} literature",
            f"Find {genre} stories",
            f"Search {genre} fiction"
        ])
    
    # General search queries
    general_queries = [
        "Find me a good book",
        "What should I read?",
        "Show me popular books",
        "Find bestsellers",
        "Search for new releases",
        "Look for trending books",
        "Find award-winning books",
        "Show me classic literature",
        "Find contemporary fiction",
        "Search for non-fiction books"
    ]
    
    queries.extend(general_queries)
    return queries

def generate_price_queries() -> List[str]:
    """Generate price-related queries."""
    queries = []
    
    for book in POPULAR_BOOKS:
        queries.extend([
            f"How much does {book} cost?",
            f"What's the price of {book}?",
            f"Show me the cost of {book}",
            f"How much is {book}?",
            f"What does {book} cost?",
            f"Price of {book}",
            f"How much for {book}?",
            f"Cost of {book} book"
        ])
    
    # Price range queries
    for price_range in PRICE_RANGES:
        queries.extend([
            f"Books {price_range}",
            f"Find books {price_range}",
            f"Show me books {price_range}",
            f"Search for books {price_range}",
            f"Look for books {price_range}"
        ])
    
    return queries

def generate_rating_queries() -> List[str]:
    """Generate rating-related queries."""
    queries = []
    
    for book in POPULAR_BOOKS:
        for term in RATING_TERMS:
            queries.extend([
                f"What's the {term} of {book}?",
                f"How is {book} {term}?",
                f"Show me the {term} for {book}",
                f"What do people think of {book}?",
                f"How good is {book}?",
                f"Rate {book}",
                f"Review of {book}",
                f"Opinion on {book}"
            ])
    
    # General rating queries
    queries.extend([
        "Highly rated books",
        "Best rated books",
        "Top rated books",
        "Books with high ratings",
        "Highly recommended books",
        "Books rated 4 stars and above",
        "Books rated 5 stars",
        "Books with 4.5 rating",
        "Top rated fiction books",
        "Best rated mystery novels"
    ])
    
    return queries

def generate_availability_queries() -> List[str]:
    """Generate availability queries."""
    queries = []
    
    for book in POPULAR_BOOKS:
        for term in AVAILABILITY_TERMS:
            queries.extend([
                f"Is {book} {term}?",
                f"Can I get {book}?",
                f"Is {book} in stock?",
                f"Availability of {book}",
                f"Can I buy {book}?",
                f"Is {book} available?",
                f"Where can I find {book}?",
                f"Can I purchase {book}?"
            ])
    
    return queries

def generate_recommendation_queries() -> List[str]:
    """Generate recommendation queries."""
    queries = []
    
    # General recommendations
    queries.extend([
        "Recommend me some books",
        "What should I read?",
        "Suggest some good books",
        "I need book recommendations",
        "What books do you recommend?",
        "Give me book suggestions",
        "What should I read next?",
        "Show me book recommendations",
        "Find me good books",
        "What are good books to read?"
    ])
    
    # Similar book recommendations
    for book in POPULAR_BOOKS:
        queries.extend([
            f"Books like {book}",
            f"Similar to {book}",
            f"Recommend books like {book}",
            f"Suggest books similar to {book}",
            f"What books are like {book}?",
            f"Find books like {book}",
            f"Show me books like {book}",
            f"Books similar to {book}"
        ])
    
    # Genre-based recommendations
    for genre in GENRES:
        queries.extend([
            f"Recommend {genre} books",
            f"Suggest {genre} novels",
            f"Good {genre} books",
            f"Best {genre} books",
            f"Top {genre} books",
            f"Popular {genre} books",
            f"Must-read {genre} books",
            f"Classic {genre} books"
        ])
    
    return queries

def generate_comparison_queries() -> List[str]:
    """Generate book comparison queries."""
    queries = []
    
    # Generate comparisons between popular books
    for i, book1 in enumerate(POPULAR_BOOKS):
        for book2 in POPULAR_BOOKS[i+1:]:
            queries.extend([
                f"Compare {book1} and {book2}",
                f"Which is better {book1} or {book2}?",
                f"{book1} vs {book2}",
                f"Compare {book1} with {book2}",
                f"Which book is better {book1} or {book2}?",
                f"Difference between {book1} and {book2}",
                f"{book1} versus {book2}",
                f"Compare {book1} to {book2}"
            ])
    
    return queries

def generate_summary_queries() -> List[str]:
    """Generate summary queries."""
    queries = []
    
    for book in POPULAR_BOOKS:
        queries.extend([
            f"Summary of {book}",
            f"Tell me about {book}",
            f"What is {book} about?",
            f"Describe {book}",
            f"Give me a summary of {book}",
            f"Brief overview of {book}",
            f"Plot of {book}",
            f"Story of {book}",
            f"Synopsis of {book}",
            f"Overview of {book}"
        ])
    
    return queries

def generate_format_queries() -> List[str]:
    """Generate format-specific queries."""
    queries = []
    
    for book in POPULAR_BOOKS:
        queries.extend([
            f"Is {book} available as ebook?",
            f"Ebook version of {book}",
            f"Digital copy of {book}",
            f"{book} ebook",
            f"Digital version of {book}",
            f"Ebook for {book}",
            f"Is {book} available as audiobook?",
            f"Audiobook version of {book}",
            f"Audio version of {book}",
            f"{book} audiobook",
            f"Audio version of {book}",
            f"Audiobook for {book}"
        ])
    
    return queries

def generate_bookstore_queries() -> List[str]:
    """Generate bookstore-specific queries."""
    queries = []
    
    for book in POPULAR_BOOKS:
        for store in BOOKSTORES:
            queries.extend([
                f"Does {store} have {book}?",
                f"{store} has {book}",
                f"Check {store} for {book}",
                f"Find {book} at {store}",
                f"Where can I buy {book}?",
                f"Which bookstore has {book}?",
                f"Where to buy {book}?",
                f"Find {book} in stores"
            ])
    
    return queries

def generate_bestseller_queries() -> List[str]:
    """Generate bestseller queries."""
    queries = []
    
    queries.extend([
        "Show me bestsellers",
        "What are the best selling books?",
        "Current bestsellers",
        "Popular books right now",
        "Trending books",
        "Top selling books",
        "Best selling books",
        "Bestseller list",
        "New York Times bestsellers",
        "Amazon bestsellers"
    ])
    
    # Genre-specific bestsellers
    for genre in GENRES:
        queries.extend([
            f"Best selling {genre} books",
            f"Bestselling {genre} novels",
            f"Current bestsellers in {genre}",
            f"Popular {genre} books",
            f"Top selling {genre} books"
        ])
    
    return queries

def generate_new_release_queries() -> List[str]:
    """Generate new release queries."""
    queries = []
    
    queries.extend([
        "New book releases",
        "Latest books",
        "Recently published books",
        "New books this year",
        "Latest releases",
        "Newest books",
        "Recent publications",
        "New book titles",
        "Just published books",
        "Fresh releases"
    ])
    
    # Genre-specific new releases
    for genre in GENRES:
        queries.extend([
            f"Recent {genre} releases",
            f"New {genre} books",
            f"Latest {genre} novels",
            f"Recent {genre} books",
            f"New {genre} publications"
        ])
    
    return queries

def generate_all_queries() -> Dict[str, List[str]]:
    """Generate all types of queries."""
    return {
        "search_queries": generate_search_queries(),
        "price_queries": generate_price_queries(),
        "rating_queries": generate_rating_queries(),
        "availability_queries": generate_availability_queries(),
        "recommendation_queries": generate_recommendation_queries(),
        "comparison_queries": generate_comparison_queries(),
        "summary_queries": generate_summary_queries(),
        "format_queries": generate_format_queries(),
        "bookstore_queries": generate_bookstore_queries(),
        "bestseller_queries": generate_bestseller_queries(),
        "new_release_queries": generate_new_release_queries()
    }

def main():
    """Generate and save test data."""
    print("Generating comprehensive test data for book chatbot...")
    
    all_queries = generate_all_queries()
    
    # Count total queries
    total_queries = sum(len(queries) for queries in all_queries.values())
    print(f"Generated {total_queries} test queries across {len(all_queries)} categories")
    
    # Save to JSON file
    with open('test_data/comprehensive_book_queries.json', 'w', encoding='utf-8') as f:
        json.dump(all_queries, f, indent=2, ensure_ascii=False)
    
    # Save individual category files
    for category, queries in all_queries.items():
        with open(f'test_data/{category}.json', 'w', encoding='utf-8') as f:
            json.dump(queries, f, indent=2, ensure_ascii=False)
    
    # Create a flat list of all queries for easy testing
    all_queries_flat = []
    for queries in all_queries.values():
        all_queries_flat.extend(queries)
    
    with open('test_data/all_queries.json', 'w', encoding='utf-8') as f:
        json.dump(all_queries_flat, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(all_queries_flat)} queries to test_data/all_queries.json")
    print("Test data generation complete!")
    
    # Print category breakdown
    print("\nCategory breakdown:")
    for category, queries in all_queries.items():
        print(f"  {category}: {len(queries)} queries")

if __name__ == "__main__":
    main()



