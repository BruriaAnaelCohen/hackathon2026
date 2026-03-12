"""
Python script to analyze books using Arcee AI and update genre in database
Database: HACKATHON2026
Table: Books
AI Model: Arcee AI (using API)
"""

import pyodbc
import urllib.request
import urllib.parse
import json
import os
from dotenv import load_dotenv

# Database connection
SERVER = '.' 
DATABASE = 'HACKATHON2026'
conn_string = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

# Arcee AI settings
MODEL_NAME = "trinity-mini"
ARCEE_API_URL = "https://api.arcee.ai/v1/chat/completions"


def connect_to_database():
    """Establish connection to SQL Server"""
    try:
        conn = pyodbc.connect(conn_string)
        print("Database connection successful!")
        return conn
    except pyodbc.Error as ex:
        print(f"Connection failed: {ex}")
        return None


def get_book_genre(api_key, book_name, author_name=None, summary=None):
    """Use AI to determine the genre of a book"""
    
    # Build context for the AI
    context = f"Book title: {book_name}"
    if author_name:
        context += f"\nAuthor: {author_name}"
    if summary:
        context += f"\nSummary: {summary}"
    
    prompt = f"""{context}

Based only on the book title above (and author/summary if provided), determine the genre/category of this book.
Respond with ONLY a single word or short phrase for the genre (e.g., Fiction, Science Fiction, Mystery, Romance, Biography, History, Fantasy, Self-Help, etc.).
Do not provide any explanation or additional text. Just the genre name."""

    try:
        # Prepare request for Arcee AI
        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 50,
            "temperature": 0.3
        }
        
        data_json = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            ARCEE_API_URL,
            data=data_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'choices' in result and len(result['choices']) > 0:
                genre = result['choices'][0]['message']['content'].strip()
                
                if genre:
                    # Clean up the response - take only the first line
                    genre = genre.split('\n')[0].strip()
                    # Remove any quotes or special characters
                    genre = genre.strip('"\'')
                
                return genre
            else:
                print(f"Unexpected response format: {result}")
                return None
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error calling Arcee AI: {e.code} - {error_body}")
        return None
    except Exception as e:
        print(f"Error calling Arcee AI: {e}")
        return None


def get_books_without_genre(conn):
    """Fetch books that don't have an AI genre yet"""
    cursor = conn.cursor()
    
    query = """
        SELECT 
            BookID, 
            BookName, 
            AuthorName, 
            ShortSummary
        FROM Books
        WHERE ai_genre IS NULL OR ai_genre = ''
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    
    return rows


def update_book_genre(conn, book_id, genre):
    """Update the ai_genre field for a book"""
    cursor = conn.cursor()
    
    query = "UPDATE Books SET ai_genre = ? WHERE BookID = ?"
    cursor.execute(query, (genre, book_id))
    conn.commit()
    
    cursor.close()


def process_books():
    """Main function to process all books without genre"""
    
    print("="*80)
    print("AI BOOK GENRE ANALYZER")
    print(f"Using AI model: {MODEL_NAME}")
    print("="*80)
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("ARCEE_API_KEY")
    
    if not api_key:
        print("Error: ARCEE_API_KEY not found in .env file!")
        return
    
    print("Arcee AI client configured successfully!")
    
    # Connect to database
    conn = connect_to_database()
    
    if not conn:
        print("Failed to connect to database. Exiting.")
        return
    
    try:
        # Get books without genre
        books = get_books_without_genre(conn)
        
        if not books:
            print("\nAll books already have genres assigned!")
            return
        
        print(f"\nFound {len(books)} book(s) without genre.\n")
        
        # Process each book
        for book in books:
            book_id = book.BookID
            book_name = book.BookName
            author_name = book.AuthorName
            summary = book.ShortSummary
            
            print(f"Processing: {book_name}")
            print(f"   Author: {author_name}")
            
            # Get genre from AI
            genre = get_book_genre(api_key, book_name, author_name, summary)
            
            if genre:
                print(f"   → Genre: {genre}")
                
                # Update database
                update_book_genre(conn, book_id, genre)
                print(f"   ✓ Updated in database\n")
            else:
                print(f"   ✗ Failed to get genre from AI\n")
        
        print("="*80)
        print("Processing complete!")
        print("="*80)
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        conn.close()


if __name__ == "__main__":
    process_books()
