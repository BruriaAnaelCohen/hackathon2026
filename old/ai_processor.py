"""
AI Data Processor Script
=======================
This script reads projects and processes from the database,
executes AI tasks for each row, and updates the database.

Usage:
    python ai_processor.py --project-id <project_id>
    python ai_processor.py  # Process all active projects
"""

import pyodbc
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===================================================================
# Configuration
# ===================================================================

# Default connection settings
DEFAULT_SERVER = '.'
DEFAULT_DATABASE = 'HACKATHON2026'

# AI API settings (using Arcee AI as default)
AI_API_URL = "https://api.arcee.ai/v1/chat/completions"
AI_MODEL = "arcee-ai/modal"


def get_connection(server_name, database_name):
    """Get database connection"""
    conn_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection=yes;'
    try:
        return pyodbc.connect(conn_string)
    except pyodbc.Error as ex:
        print(f"Connection failed: {ex}")
        return None


def get_active_projects(conn, project_name=None):
    """Get active projects from database by name"""
    cursor = conn.cursor()
    
    if project_name:
        cursor.execute("""
            SELECT ProjectID, ProjectName, ServerName, DatabaseName, TableName, Description
            FROM AI_Projects 
            WHERE ProjectName = ? AND Status = 'Active'
        """, (project_name,))
    else:
        cursor.execute("""
            SELECT ProjectID, ProjectName, ServerName, DatabaseName, TableName, Description
            FROM AI_Projects 
            WHERE Status = 'Active'
        """)
    
    projects = cursor.fetchall()
    cursor.close()
    return projects


def get_processes(conn, project_id):
    """Get all processes for a project"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ProcessID, ProcessType, TaskDescription, SourceColumn, 
               SourceColumnDescription, AdditionalColumns, MaxCategories
        FROM AI_Processes 
        WHERE ProjectID = ?
        ORDER BY CreatedDate
    """, (project_id,))
    
    processes = cursor.fetchall()
    cursor.close()
    return processes


def get_categories_for_process(conn, process_id):
    """Get categories for a categorization process"""
    cursor = conn.cursor()
    
    cursor.execute("SELECT CategoryName FROM AI_Categories WHERE ProcessID = ?", (process_id,))
    categories = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return categories


def get_table_data(conn, table_name, source_column, additional_columns=None, limit=None):
    """Get data from the source table"""
    cursor = conn.cursor()
    
    columns = [source_column]
    if additional_columns:
        columns.extend(additional_columns)
    
    column_str = ', '.join(columns)
    query = f"SELECT {column_str} FROM {table_name} WHERE {source_column} IS NOT NULL"
    
    if limit:
        query += f" TOP {limit}"
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error fetching data: {e}")
        cursor.close()
        return []


def call_ai_api(prompt, api_key):
    """Call AI API to get response"""
    try:
        data = {
            "model": AI_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        data_json = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            AI_API_URL,
            data=data_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            return None
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error: {e.code} - {error_body}")
        return None
    except Exception as e:
        print(f"Error calling AI: {e}")
        return None


def categorize_value(value, categories, task_description):
    """Categorize a single value using the predefined categories"""
    api_key = os.getenv("ARCEE_API_KEY")
    
    if not api_key:
        print("Error: ARCEE_API_KEY not found in .env file!")
        return None
    
    prompt = f"""
Task: {task_description}

Value to categorize: {value}

Available categories: {', '.join(categories)}

Based on the task and value above, select the most appropriate category from the available categories.
Respond with ONLY the category name, nothing else.
"""
    
    result = call_ai_api(prompt, api_key)
    
    if result:
        # Clean up response - find matching category
        result_clean = result.strip().strip('"\'')
        for cat in categories:
            if cat.lower() in result_clean.lower() or result_clean.lower() in cat.lower():
                return cat
    
    return None


def enrich_value(values_dict, task_description, expected_output):
    """Enrich data using AI"""
    api_key = os.getenv("ARCEE_API_KEY")
    
    if not api_key:
        print("Error: ARCEE_API_KEY not found in .env file!")
        return None
    
    # Build context from values
    context = "Given data:\n"
    for key, val in values_dict.items():
        context += f"- {key}: {val}\n"
    
    prompt = f"""
{context}

Task: {task_description}

Expected output: {expected_output}

Based on the given data and task, provide the expected enrichment information.
Respond with ONLY the answer, no explanation needed.
"""
    
    return call_ai_api(prompt, api_key)


def add_output_column(conn, table_name, process_type):
    """Add output column to the table if it doesn't exist"""
    cursor = conn.cursor()
    
    # Determine column name based on process type
    if process_type == 'Categorize':
        col_name = 'ai_category'
    else:
        col_name = 'ai_enriched'
    
    try:
        # Check if column exists
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{col_name}'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Add column
            cursor.execute(f"ALTER TABLE {table_name} ADD {col_name} NVARCHAR(500)")
            conn.commit()
            print(f"Added column '{col_name}' to table '{table_name}'")
        
        cursor.close()
        return col_name
        
    except Exception as e:
        print(f"Error adding column: {e}")
        cursor.close()
        return None


def update_row(conn, table_name, source_column, output_column, source_value, output_value):
    """Update a row in the database"""
    cursor = conn.cursor()
    
    try:
        query = f"UPDATE {table_name} SET {output_column} = ? WHERE {source_column} = ?"
        cursor.execute(query, (output_value, source_value))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error updating row: {e}")
        cursor.close()
        return False


def process_project(project):
    """Process a single project"""
    project_id, project_name, server_name, db_name, table_name, description = project
    
    print(f"\n{'='*60}")
    print(f"Processing Project: {project_name} (ID: {project_id})")
    print(f"Table: {table_name}")
    print(f"{'='*60}")
    
    # Connect to the project's database
    conn = get_connection(server_name, db_name)
    if not conn:
        print(f"Failed to connect to database {db_name}")
        return
    
    try:
        # Get processes for this project
        processes = get_processes(conn, project_id)
        
        if not processes:
            print("No active processes found for this project")
            return
        
        # Process each process
        for proc in processes:
            process_id, process_type, task_desc, source_col, source_desc, add_cols_json, max_cats = proc
            
            print(f"\n--- Process: {process_type} ---")
            print(f"Task: {task_desc}")
            print(f"Source Column: {source_col}")
            
            # Parse additional columns
            additional_columns = json.loads(add_cols_json) if add_cols_json else []
            
            # Add output column to table
            output_column = add_output_column(conn, table_name, process_type)
            if not output_column:
                print("Failed to add output column, skipping...")
                continue
            
            # Get categories for categorization
            categories = []
            if process_type == 'Categorize':
                categories = get_categories_for_process(conn, process_id)
                print(f"Categories: {', '.join(categories)}")
            
            # Get data from table
            rows = get_table_data(conn, table_name, source_col, additional_columns)
            print(f"Found {len(rows)} rows to process")
            
            # Process each row
            for i, row in enumerate(rows):
                source_value = row[0]
                values_dict = {source_col: source_value}
                
                # Build values dict with additional columns
                for j, col in enumerate(additional_columns):
                    if j + 1 < len(row):
                        values_dict[col] = row[j + 1]
                
                # Process based on type
                if process_type == 'Categorize':
                    result = categorize_value(source_value, categories, task_desc)
                else:
                    result = enrich_value(values_dict, task_desc, None)
                
                # Update database
                if result:
                    update_row(conn, table_name, source_col, output_column, source_value, result)
                    print(f"  [{i+1}/{len(rows)}] Processed: {source_value} -> {result}")
                else:
                    print(f"  [{i+1}/{len(rows)}] Failed: {source_value}")
        
        print(f"\n✅ Project {project_id} processing complete!")
        
    finally:
        conn.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Data Processor')
    parser.add_argument('--project-name', type=str, help='Project name to process')
    parser.add_argument('--server', default=DEFAULT_SERVER, help='Server name')
    parser.add_argument('--database', default=DEFAULT_DATABASE, help='Database name')
    
    args = parser.parse_args()
    
    print("="*60)
    print("AI Data Processor")
    print("="*60)
    
    # Connect to metadata database
    conn = get_connection(args.server, args.database)
    if not conn:
        print("Failed to connect to database!")
        return
    
    try:
        # Get projects to process
        projects = get_active_projects(conn, args.project_name)
        
        if not projects:
            print(f"No project found with name: {args.project_name}")
            return
        
        print(f"Found {len(projects)} project(s) to process")
        
        # Process each project
        for project in projects:
            process_project(project)
    
    finally:
        conn.close()
    
    print("\n" + "="*60)
    print("All processing complete!")
    print("="*60)


if __name__ == "__main__":
    main()
