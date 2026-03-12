"""
Python script to analyze books using Google Gemini AI and update genre in database
Database: HACKATHON2026
Table: Books
AI Model: Google Gemini 3 Flash (Free)
"""

import pyodbc
from google import genai
import os
from dotenv import load_dotenv

# Database connection
SERVER = '.' 
DATABASE = 'HACKATHON2026'
conn_string = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

# Google Gemini settings
MODEL_NAME = "gemini-3-flash-preview"


def connect_to_database():
    """Establish connection to SQL Server"""
    try:
        conn = pyodbc.connect(conn_string)
        print("Database connection successful!")
        return conn
    except pyodbc.Error as ex:
        print(f"Connection failed: {ex}")
        return None


def get_book_genre(client, book_name, author_name=None, summary=None):
    """Use AI to determine the genre of a book"""
    
    # Build context for the AI
    context = f"Book title: {book_name}"
    if author_name:
        context += f"\nAuthor: {author_name}"
    if summary:
        context += f"\nSummary: {summary}"
    
    prompt = f"""{context}

Basond ed only on the book title above (and author/summary if provided), determine the genre/category of this book.
Respwith ONLY a single word or short phrase for the genre (e.g., Fiction, Science Fiction, Mystery, Romance, Biography, History, Fantasy, Self-Help, etc.).
Do not provide any explanation or additional text. Just the genre name."""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        
        genre = response.text.strip() if response.text else None
        
        if genre:
            # Clean up the response - take only the first line
            genre = genre.split('\n')[0].strip()
            # Remove any quotes or special characters
            genre = genre.strip('"\'')
        
        return genre
        
    except Exception as e:
        print(f"Error calling Gemini: {e}")
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
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env file!")
        return

    # Initialize Gemini client
    try:
        client = genai.Client(api_key=api_key)
        print("Gemini client initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")
        print("Make sure you have configured your Google API key.")
        return
    
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
            genre = get_book_genre(client, book_name, author_name, summary)
            
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
