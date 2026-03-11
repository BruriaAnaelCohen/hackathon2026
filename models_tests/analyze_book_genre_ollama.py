"""
Python script to analyze books using Ollama AI (local) and update genre in database
Database: HACKATHON2026
Table: Books
AI Model: Ollama (mistral) - Runs locally, no API limits
"""

import pyodbc
import urllib.request
import urllib.error
import json
import time

# Database connection
SERVER = '.' 
DATABASE = 'HACKATHON2026'
conn_string = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"

# Available models - uncomment the one you want to use:
# MODEL_NAME = "llama3"          # Fast, good quality
# MODEL_NAME = "mistral"        # Smaller, faster
# MODEL_NAME = "phi3"           # Very small, fastest
# MODEL_NAME = "llama2"         # Older version
MODEL_NAME = "llama3"  # Currently using


def connect_to_database():
    """Establish connection to SQL Server"""
    try:
        conn = pyodbc.connect(conn_string)
        print("Database connection successful!")
        return conn
    except pyodbc.Error as ex:
        print(f"Connection failed: {ex}")
        return None


def check_ollama():
    """Check if Ollama is running and available models"""
    print("Checking Ollama connection...")
    try:
        # First check if server is running
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/")
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Ollama server responded: {response.status}")
    except Exception as e:
        print(f"Cannot connect to Ollama server: {e}")
        print("Make sure Ollama is running (run 'ollama serve' in terminal)")
        return False
    
    try:
        # Then check available models
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=30) as response:
            models = json.loads(response.read().decode('utf-8'))
            print("Available Ollama models:")
            for m in models.get('models', []):
                print(f"  - {m.get('name', 'Unknown')}")
            return True
    except Exception as e:
        print(f"Error getting models: {e}")
        return False


def check_ollama_llama3():
    """Simple check - just verify server is running, use llama3 directly"""
    print(f"Checking Ollama for {MODEL_NAME}...")
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/")
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Ollama server is running: {response.status}")
            return True
    except Exception as e:
        print(f"Cannot connect to Ollama: {e}")
        return False


def get_book_genre(book_name, author_name=None, summary=None):
    """Use AI to determine the genre of a book"""
    
    # Build context for the AI
    context = f"Book title: {book_name}"
    if author_name:
        context += f"\nAuthor: {author_name}"
    if summary:
        context += f"\nSummary: {summary}"
    
    prompt = f"""{context}

Based only on the book title above (and author/summary if provided), determine the genre/category of this book.
 single word or shortRespond with ONLY a phrase for the genre (e.g., Fiction, Science Fiction, Mystery, Romance, Biography, History, Fantasy, Self-Help, etc.).
Do not provide any explanation or additional text. Just the genre name."""

    try:
        url = f"{OLLAMA_BASE_URL}/api/generate"
        data = json.dumps({
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            genre = result.get("response", "").strip()
            
            if genre:
                # Clean up the response - take only the first line
                genre = genre.split('\n')[0].strip()
                # Remove any quotes or special characters
                genre = genre.strip('"\'')
            
            return genre
            
    except urllib.error.URLError as e:
        print(f"Error: Cannot connect to Ollama. Make sure Ollama is running.")
        print(f"Details: {e}")
        return None
    except Exception as e:
        print(f"Error calling Ollama: {e}")
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
    print("AI BOOK GENRE ANALYZER (Ollama)")
    print(f"Using AI model: {MODEL_NAME}")
    print("Make sure Ollama is running on localhost:11434")
    print("="*80)
    
    # Check if Ollama is running
    if not check_ollama_llama3():
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
        
        # Start total timer
        total_start_time = time.time()
        
        # Process each book
        for i, book in enumerate(books):
            book_start_time = time.time()
            
            book_id = book.BookID
            book_name = book.BookName
            author_name = book.AuthorName
            summary = book.ShortSummary
            
            print(f"[{i+1}/{len(books)}] Processing: {book_name}")
            print(f"   Author: {author_name}")
            
            # Get genre from AI
            genre = get_book_genre(book_name, author_name, summary)
            
            if genre:
                print(f"   -> Genre: {genre}")
                
                # Update database
                update_book_genre(conn, book_id, genre)
                print(f"   OK Updated in database")
            else:
                print(f"   X Failed to get genre from AI")
            
            # Print time for this book
            book_elapsed = time.time() - book_start_time
            print(f"   [Time: {book_elapsed:.1f} seconds]")
        
        print("="*80)
        
        # Calculate total time
        total_elapsed = time.time() - total_start_time
        total_minutes = total_elapsed / 60
        
        print(f"Processing complete!")
        print(f"Total time: {total_elapsed:.1f} seconds ({total_minutes:.2f} minutes)")
        print("="*80)
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        conn.close()


if __name__ == "__main__":
    process_books()
