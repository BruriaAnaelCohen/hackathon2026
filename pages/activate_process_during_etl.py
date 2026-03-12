"""
Activate Process Script - Run AI on specific table
==================================================
Input: table_name, dest_column
Finds project/process by this unique pair
For Categorize: loops over rows, calls AI, updates dest column
For Enrich: TODO
"""

import pyodbc
import urllib.request
import urllib.error
import json
import time
from db_utils import connect_to_database, get_categories


# Database (hardcoded - same DB always)
SERVER = "."
DATABASE = "HACKATHON2026"

# Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3"


def connect():
    """Connect to database"""
    conn_str = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"DB Error: {e}")
        return None


def check_ollama():
    """Check if Ollama is running"""
    try:
        urllib.request.urlopen(f"{OLLAMA_BASE_URL}/", timeout=5)
        return True
    except:
        return False


def get_process_by_table_dest(table_name, dest_column):
    """Find project and process by table_name + dest_column (unique pair)"""
    conn = connect()
    if not conn:
        return None, None
    
    cursor = conn.cursor()
    
    # Find process by table name and dest column
    query = """
        SELECT p.ProjectID, p.ProjectName, p.TableName, 
               c.ProcessID, c.ProcessType, c.SourceColumn, c.DestColumn, c.TaskDescription
        FROM AI_Projects p
        JOIN AI_Processes c ON p.ProjectID = c.ProjectID
        WHERE p.TableName = ? AND c.DestColumn = ?
    """
    
    cursor.execute(query, (table_name, dest_column))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        project = {
            'project_id': row[0],
            'project_name': row[1],
            'table_name': row[2]
        }
        process = {
            'process_id': row[3],
            'process_type': row[4],
            'source_column': row[5],
            'dest_column': row[6],
            'task_description': row[7]
        }
        return project, process
    
    return None, None


def get_table_columns(table_name):
    """Get all column names for a table"""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
    columns = [col[0] for col in cursor.description]
    conn.close()
    return columns


def get_rows_to_process(table_name, dest_column):
    """Get all rows where dest column is NULL or empty"""
    conn = connect()
    cursor = conn.cursor()
    
    query = f"SELECT * FROM {table_name} WHERE {dest_column} IS NULL OR {dest_column} = ''"
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except:
        # If query fails, get all rows
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        conn.close()
        return rows


def update_value(table_name, dest_column, row_index, new_value):
    """Update dest column for a specific row by index"""
    conn = connect()
    cursor = conn.cursor()
    
    # Use ROW_NUMBER() to identify rows
    query = f"""
        UPDATE t SET {dest_column} = ?
        FROM (SELECT *, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as RowNum FROM {table_name}) t
        WHERE t.RowNum = ?
    """
    
    try:
        cursor.execute(query, (new_value, row_index + 1))  # 1-based index
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"   Update error: {e}")
        conn.close()
        return False


def call_ollama(prompt):
    """Send prompt to Ollama and get response"""
    try:
        url = f"{OLLAMA_BASE_URL}/api/generate"
        data = json.dumps({
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result.get("response", "").strip()
            return text.split('\n')[0].strip().strip('"\'')
            
    except Exception as e:
        print(f"   Ollama error: {e}")
        return None


def categorize(value, categories, source_column):
    """Categorize a value using AI"""
    
    categories_list = ", ".join([f"'{cat}'" for cat in categories])
    
    prompt = f"""
Categorize the following value from column '{source_column}' into ONE of these categories: {categories_list}

Value: {value}

Respond ONLY with the category name. No explanation.
"""
    
    result = call_ollama(prompt)
    
    if result:
        # Validate it's one of the categories
        result_lower = result.lower()
        for cat in categories:
            if cat.lower() == result_lower:
                return cat
    
    return None


def run_process(table_name, dest_column):
    """Main function - run process for table_name + dest_column"""
    
    print("=" * 50)
    print(f"🚀 Activating Process")
    print(f"   Table: {table_name}")
    print(f"   Dest Column: {dest_column}")
    print("=" * 50)
    
    # Check Ollama
    if not check_ollama():
        print("❌ Ollama not running! Start with: ollama serve")
        return
    
    # Find project and process
    project, process = get_process_by_table_dest(table_name, dest_column)
    
    if not project or not process:
        print(f"❌ No process found for table '{table_name}' with dest column '{dest_column}'")
        return
    
    print(f"✅ Found project: {project['project_name']}")
    print(f"   Process Type: {process['process_type']}")
    print(f"   Source Column: {process['source_column']}")
    
    # For now, only Categorize
    if process['process_type'] != "Categorize":
        print("❌ Only Categorize processes are supported for now")
        return
    
    # Get categories for this process
    categories = get_categories(SERVER, DATABASE, process['process_id'])
    
    if not categories:
        print(f"❌ No categories found for this process")
        return
    
    print(f"   Categories: {categories}")
    
    # Get rows to process
    rows = get_rows_to_process(table_name, dest_column)
    
    if not rows:
        print(f"✅ All rows already have values!")
        return
    
    print(f"\n📊 Found {len(rows)} row(s) to process")
    
    # Get column names
    columns = get_table_columns(table_name)
    source_col = process['source_column']
    source_idx = columns.index(source_col)
    
    processed = 0
    
    # Process each row
    for i, row in enumerate(rows):
        value = row[source_idx]
        
        if not value:
            print(f"[{i+1}/{len(rows)}] Skipping empty value")
            continue
        
        print(f"[{i+1}/{len(rows)}] '{value}'")
        
        # Call AI
        category = categorize(value, categories, source_col)
        
        if category:
            print(f"   -> {category}")
            # Update database
            if update_value(table_name, dest_column, i, category):
                print(f"   ✅ Updated")
                processed += 1
            else:
                print(f"   ❌ Failed to update")
        else:
            print(f"   ❌ AI failed")
        
        # Small delay
        time.sleep(0.3)
    
    print(f"\n{'='*50}")
    print(f"🎉 Done! Processed {processed}/{len(rows)} rows")
    print(f"{'='*50}")


if __name__ == "__main__":
    # import sys
    
    # if len(sys.argv) < 3:
    #     print("Usage: python activate_process.py <table_name> <dest_column>")
    #     print("Example: python activate_process.py Books ai_genre")
    #     sys.exit(1)
    
    table_name = "Books" #sys.argv[1]
    dest_column =  "ai_genre" # sys.argv[2]
    
    run_process(table_name, dest_column)

    table_name = "Books" #sys.argv[1]
    dest_column =  "ai_target_audience" # sys.argv[2]
    
    run_process(table_name, dest_column)
