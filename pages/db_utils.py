"""
Database utility functions for AI Enrichment Tool
"""

import pyodbc
import json


def get_connection(server_name='.'):
    """Get database connection"""
    try:
        conn_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE=master;Trusted_Connection=yes;'
        
        return pyodbc.connect(conn_string)
    except:
        return None


def connect_to_database(server_name, database_name):
    """Connect to a specific database"""
    try:
        conn_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection=yes;'
        
        return pyodbc.connect(conn_string)
    except pyodbc.Error as ex:
        return None


def get_databases(server_name):
    """Get list of databases on the server"""
    conn = get_connection(server_name)
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.databases WHERE state = 0 ORDER BY name")
    databases = [row[0] for row in cursor.fetchall()]
    conn.close()

    return databases


def get_tables(server_name, database_name):
    """Get list of tables in a database"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return tables


def get_columns(server_name, database_name, table_name):
    """Get list of columns in a table"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return []
    
    cursor = conn.cursor()
    query = f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' ORDER BY ORDINAL_POSITION"
    cursor.execute(query)
    columns = [(row[0], row[1]) for row in cursor.fetchall()]
    conn.close()
    
    return columns


def save_project_to_db(server_name, database_name, project_name, description, table_name):
    """Save project to AI_Projects table"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    # First insert the project
    cursor.execute("""
        INSERT INTO AI_Projects (ProjectName, ServerName, DatabaseName, TableName, Description, CreatedDate, Status)
        VALUES (?, ?, ?, ?, ?, GETDATE(), 'Active')
    """, (project_name, server_name, database_name, table_name, description))
    
    # Then get the ID
    cursor.execute("SELECT @@IDENTITY as ProjectID")
    row = cursor.fetchone()
    project_id = int(row[0]) if row and row[0] is not None else None
    
    conn.commit()
    conn.close()
    
    return project_id


def save_process_to_db(server_name, database_name, project_id, process_type, task_description, 
                       source_column, source_column_description, dest_column_name,
                       additional_columns, max_categories):
    """Save process to AI_Processes table"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return None
    
    additional_cols_json = json.dumps(additional_columns) if additional_columns else None
    
    cursor = conn.cursor()
    
    # First insert the process
    cursor.execute("""
        INSERT INTO AI_Processes (ProjectID, ProcessType, TaskDescription, SourceColumn, 
                                  SourceColumnDescription, DestColumn, AdditionalColumns, 
                                  MaxCategories, CreatedDate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
    """, (project_id, process_type, task_description, source_column, 
          source_column_description, dest_column_name, additional_cols_json, max_categories))
    
    # Then get the ID
    cursor.execute("SELECT @@IDENTITY as ProcessID")
    row = cursor.fetchone()
    process_id = int(row[0]) if row and row[0] is not None else None
    
    conn.commit()
    conn.close()
    
    return process_id


def save_categories_to_db(server_name, database_name, process_id, categories):
    """Save categories to AI_Categories table"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return False
    
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM AI_Categories
    WHERE ProcessID = ?
    """, process_id)

    for category in categories:
        cursor.execute("INSERT INTO AI_Categories (ProcessID, CategoryName) VALUES (?, ?)", (process_id, category))
    
    conn.commit()
    conn.close()
    return True


def get_projects(server_name, database_name):
    """Get all projects from the database"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute("SELECT ProjectID, ProjectName, TableName, Description, CreatedDate, Status FROM AI_Projects ORDER BY CreatedDate DESC")
    projects = cursor.fetchall()
    conn.close()
    
    return projects


def get_processes(server_name, database_name, project_id):
    """Get all processes for a project"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ProcessID, ProcessType, TaskDescription, SourceColumn, SourceColumnDescription,
               DestColumn, AdditionalColumns, MaxCategories
        FROM AI_Processes 
        WHERE ProjectID = ?
        ORDER BY CreatedDate
    """, (project_id,))
    processes = cursor.fetchall()
    conn.close()
    
    return processes


def get_categories(server_name, database_name, process_id):
    """Get all categories for a process"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute("SELECT CategoryName FROM AI_Categories WHERE ProcessID = ?", (process_id,))
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return categories
