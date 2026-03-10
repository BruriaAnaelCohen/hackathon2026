"""
Python script to connect to SQL Server and read from Books table
Database: HACKATHON2026
Table: Books
"""

import pyodbc

SERVER = '.' 
DATABASE = 'HACKATHON2026'

conn_string = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'


def connect_to_database():
    """Establish connection to SQL Server"""
    try:
        conn = pyodbc.connect(conn_string)
        print("Connection successful!")
        return conn
    except pyodbc.Error as ex:
        print(f"Connection failed: {ex}")
        return None


def read_books_table(conn):
    """Read all data from Books table"""
    cursor = conn.cursor()
    
    # Query to select all books
    query = """
        SELECT 
            BookID, 
            BookName, 
            AuthorName, 
            PublishYear, 
            ShortSummary, 
            GeneralReview, 
            Rating,
            ai_genre,
            ai_is_favorite,
            ai_target_audience
        FROM Books
    """
    
    cursor.execute(query)
    
    # Get column names
    columns = [column[0] for column in cursor.description]
    print("\n" + "="*80)
    print("BOOKS TABLE DATA")
    print("="*80)
    print(f"Columns: {', '.join(columns)}")
    print("-"*80)
    
    # Fetch all rows
    rows = cursor.fetchall()
    
    # Print each row
    for row in rows:
        print(f"\nBook ID: {row.BookID}")
        print(f"   Title: {row.BookName}")
        print(f"   Author: {row.AuthorName}")
        print(f"   Year: {row.PublishYear}")
        print(f"   Summary: {row.ShortSummary[:100] if row.ShortSummary else 'N/A'}...")
        print(f"   Review: {row.GeneralReview[:100] if row.GeneralReview else 'N/A'}...")
        print(f"   Rating: {row.Rating}")
        print(f"   AI Genre: {row.ai_genre}")
        print(f"   AI Favorite: {row.ai_is_favorite}")
        print(f"   AI Target Audience: {row.ai_target_audience}")
    
    print("\n" + "="*80)
    print(f"Total books found: {len(rows)}")
    print("="*80)
    
    cursor.close()
    return rows


def read_books_as_list(conn):
    """Read books and return as list of dictionaries"""
    cursor = conn.cursor()
    
    query = """
        SELECT 
            BookID, BookName, AuthorName, PublishYear, 
            ShortSummary, GeneralReview, Rating,
            ai_genre, ai_is_favorite, ai_target_audience
        FROM Books
    """
    
    cursor.execute(query)
    
    books = []
    columns = [column[0] for column in cursor.description]
    
    for row in cursor.fetchall():
        book = dict(zip(columns, row))
        books.append(book)
    
    cursor.close()
    return books


def main():
    """Main function to run the script"""
    print("Connecting to SQL Server...")
    print(f"   Server: {SERVER}")
    print(f"   Database: {DATABASE}")
    
    conn = connect_to_database()
    
    if conn:
        try:
            # Option 1: Display formatted results
            read_books_table(conn)
            
            # Option 2: Get data as list of dictionaries
            # books_list = read_books_as_list(conn)
            # print("\nBooks as list:")
            # for book in books_list:
            #     print(book)
            
        finally:
            conn.close()
    else:
        print("Please check your connection settings.")


if __name__ == "__main__":
    main()
