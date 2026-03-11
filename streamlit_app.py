"""
AI Data Enrichment Tool - Streamlit UI
=======================================
A generic tool to help developers connect to AI models and enrich their data.

Features:
- Create projects with database connection details
- Define categorization tasks (classify data into categories)
- Define enrichment tasks (add additional info based on data)
- Generate categories using AI
- Process data and update database

Database: Uses SQL Server with AI_Projects, AI_Processes, AI_Categories tables
"""

import streamlit as st
import pyodbc
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===================================================================
# Database Connection Functions
# ===================================================================

def get_connection(server_name='.'):
    """Get database connection"""
    try:
        # First try trusted connection, then with credentials
        conn_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE=master;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_string)
        return conn
    except:
        # Try with SQL auth if trusted fails
        return None


def connect_to_database(server_name, database_name):
    """Connect to a specific database"""
    try:
        conn_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_string)
        return conn
    except pyodbc.Error as ex:
        st.error(f"Connection failed: {ex}")
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
    query = f"""
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
    """
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
    cursor.execute("""
        INSERT INTO AI_Projects (ProjectName, ServerName, DatabaseName, TableName, Description, CreatedDate, Status)
        VALUES (?, ?, ?, ?, ?, GETDATE(), 'Active');
        SELECT SCOPE_IDENTITY() as ProjectID;
    """, (project_name, server_name, database_name, table_name, description))
    
    row = cursor.fetchone()
    project_id = row[0] if row else None
    conn.commit()
    conn.close()
    return project_id


def save_process_to_db(server_name, database_name, project_id, process_type, task_description, 
                       source_column, source_column_description, additional_columns,
                       expected_output, max_categories):
    """Save process to AI_Processes table"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return None
    
    additional_cols_json = json.dumps(additional_columns) if additional_columns else None
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO AI_Processes (ProjectID, ProcessType, TaskDescription, SourceColumn, 
                                  SourceColumnDescription, AdditionalColumns, ExpectedOutput, 
                                  MaxCategories, CreatedDate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE());
        SELECT SCOPE_IDENTITY() as ProcessID;
    """, (project_id, process_type, task_description, source_column, 
          source_column_description, additional_cols_json, expected_output, max_categories))
    
    row = cursor.fetchone()
    process_id = row[0] if row else None
    conn.commit()
    conn.close()
    return process_id


def save_categories_to_db(server_name, database_name, process_id, categories):
    """Save categories to AI_Categories table"""
    conn = connect_to_database(server_name, database_name)
    if not conn:
        return False
    
    cursor = conn.cursor()
    for category in categories:
        cursor.execute("""
            INSERT INTO AI_Categories (ProcessID, CategoryName)
            VALUES (?, ?)
        """, (process_id, category))
    
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
               AdditionalColumns, ExpectedOutput, MaxCategories
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


# ===================================================================
# AI Helper Functions
# ===================================================================

def generate_categories_ai(column_data, source_column_description, max_categories):
    """Use AI to generate category suggestions based on column data"""
    # This is a placeholder - in production, connect to actual AI API
    # For now, return sample categories based on data analysis
    
    sample_prompt = f"""
    Analyze the following values from a database column and suggest {max_categories if max_categories else 10} appropriate categories:
    
    Values: {', '.join(str(v) for v in column_data[:20])}
    Column description: {source_column_description or 'Not provided'}
    
    Return a JSON array of category names.
    """
    
    # Return sample categories based on data patterns
    unique_values = set(str(v).strip() for v in column_data if v)
    
    # Simple heuristics for demo
    if any(word in str(column_data[0]).lower() for word in ['job', 'title', 'position', 'role']):
        return ['Programmer', 'Manager', 'Analyst', 'Designer', 'Engineer', 'Consultant', 'Administrator', 'Director']
    elif any(word in str(column_data[0]).lower() for word in ['city', 'country', 'location']):
        return ['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Oceania']
    elif any(word in str(column_data[0]).lower() for word in ['category', 'type', 'kind']):
        return ['Category A', 'Category B', 'Category C', 'Category D']
    else:
        # Extract unique first words as categories
        categories = list(unique_values)[:max_categories if max_categories else 10]
        return categories if categories else ['Category 1', 'Category 2', 'Category 3']


# ===================================================================
# Streamlit UI
# ===================================================================

st.set_page_config(
    page_title="AI Data Enrichment Tool",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'project_id' not in st.session_state:
    st.session_state.project_id = None
if 'server_name' not in st.session_state:
    st.session_state.server_name = '.'
if 'database_name' not in st.session_state:
    st.session_state.database_name = 'HACKATHON2026'

st.title("🤖 AI Data Enrichment Tool")
st.markdown("---")

# ===================================================================
# Sidebar - Database Connection
# ===================================================================
st.sidebar.header("🔌 Database Connection")

server_name = st.sidebar.text_input(
    "Server Name",
    value=st.session_state.server_name,
    help="SQL Server instance name (e.g., localhost or .)"
)

database_name = st.sidebar.text_input(
    "Database Name",
    value=st.session_state.database_name,
    help="Database containing your data"
)

# Test connection
if st.sidebar.button("🔗 Test Connection"):
    conn = connect_to_database(server_name, database_name)
    if conn:
        st.sidebar.success("✅ Connection successful!")
        conn.close()
    else:
        st.sidebar.error("❌ Connection failed")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Quick Links")
if st.sidebar.button("📊 View Existing Projects"):
    st.session_state.view_projects = True
    st.rerun()

# ===================================================================
# Main Content
# ===================================================================

# Check if viewing existing projects
if st.session_state.get('view_projects', False):
    st.header("📊 Existing Projects")
    
    projects = get_projects(server_name, database_name)
    
    if not projects:
        st.info("No projects found. Create your first project below!")
        st.session_state.view_projects = False
        st.rerun()
    else:
        for proj in projects:
            with st.expander(f"📁 {proj[1]} (ID: {proj[0]})"):
                st.write(f"**Table:** {proj[2]}")
                st.write(f"**Description:** {proj[3] or 'N/A'}")
                st.write(f"**Created:** {proj[4]}")
                st.write(f"**Status:** {proj[5]}")
                
                # Show processes for this project
                processes = get_processes(server_name, database_name, proj[0])
                if processes:
                    st.write("**Processes:**")
                    for proc in processes:
                        st.write(f"  - {proc[1]}: {proc[2]} (Source: {proc[3]})")
        
    if st.button("← Back to Create Project"):
        st.session_state.view_projects = False
        st.rerun()
    
    st.stop()

# ===================================================================
# Step 1: Project Setup
# ===================================================================
st.header("📝 Step 1: Create New Project")

col1, col2 = st.columns(2)

with col1:
    project_name = st.text_input(
        "Project Name *",
        placeholder="e.g., Job Classification Project",
        help="Give your project a descriptive name"
    )

with col2:
    table_name = st.text_input(
        "Target Table Name *",
        placeholder="e.g., Employees, Products, Jobs",
        help="The table containing data to enrich"
    )

project_description = st.text_area(
    "Description (Optional)",
    placeholder="Brief description of what you're trying to accomplish...",
    help="Optional - helps you remember the project's purpose"
)

# Get columns for the table
columns = []
if table_name:
    columns = get_columns(server_name, database_name, table_name)
    if columns:
        st.success(f"✅ Found {len(columns)} columns in table '{table_name}'")
    else:
        st.warning(f"⚠️ Could not find columns for table '{table_name}'. Make sure the table exists.")

st.markdown("---")

# ===================================================================
# Step 2: Define Processes
# ===================================================================
st.header("⚙️ Step 2: Define Processes")

# Initialize processes in session state
if 'processes' not in st.session_state:
    st.session_state.processes = []

# Add new process button
if st.button("➕ Add Process"):
    st.session_state.processes.append({
        'type': 'Categorize',
        'task_description': '',
        'source_column': '',
        'source_column_description': '',
        'additional_columns': [],
        'expected_output': '',
        'max_categories': 10,
        'categories': []
    })
    st.rerun()

# Display processes
for i, proc in enumerate(st.session_state.processes):
    with st.expander(f"Process {i+1}: {proc['type']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            proc['type'] = st.selectbox(
                f"Process Type #{i+1}",
                ['Categorize', 'Enrich'],
                index=0 if proc['type'] == 'Categorize' else 1,
                key=f"type_{i}"
            )
        
        with col2:
            if columns:
                column_options = [c[0] for c in columns]
                proc['source_column'] = st.selectbox(
                    f"Source Column #{i+1}",
                    column_options,
                    index=column_options.index(proc['source_column']) if proc['source_column'] in column_options else 0,
                    key=f"source_{i}"
                )
            else:
                proc['source_column'] = st.text_input(
                    f"Source Column Name #{i+1}",
                    value=proc['source_column'],
                    key=f"source_{i}"
                )
        
        # Common fields
        proc['task_description'] = st.text_area(
            f"What do you want to accomplish? (Task Description) #{i+1}",
            value=proc['task_description'],
            placeholder="e.g., Classify jobs into professional categories",
            key=f"task_{i}"
        )
        
        proc['source_column_description'] = st.text_input(
            f"Column Description (Optional) #{i+1}",
            value=proc['source_column_description'],
            placeholder="e.g., Job titles like 'Software Engineer', 'Data Analyst'",
            key=f"desc_{i}"
        )
        
        # Type-specific fields
        if proc['type'] == 'Categorize':
            # Additional columns for context
            other_columns = [c[0] for c in columns if c[0] != proc['source_column']] if columns else []
            if other_columns:
                proc['additional_columns'] = st.multiselect(
                    f"Additional columns for context (optional) #{i+1}",
                    other_columns,
                    default=proc['additional_columns'],
                    key=f"additional_{i}"
                )
            
            proc['expected_output'] = st.text_input(
                "What category values do you expect?",
                value=proc['expected_output'],
                placeholder="e.g., Cleaner, Programmer, Manager (single word or short phrase)",
                key=f"output_{i}"
            )
            
            proc['max_categories'] = st.number_input(
                "Maximum number of categories",
                min_value=2,
                max_value=50,
                value=proc['max_categories'],
                key=f"max_{i}"
            )
            
            # Generate categories button
            if st.button(f"🎯 Generate Categories with AI #{i+1}", key=f"gen_cat_{i}"):
                if proc['source_column'] and table_name:
                    # Get sample data from column
                    conn = connect_to_database(server_name, database_name)
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT DISTINCT TOP 20 {proc['source_column']} FROM {table_name} WHERE {proc['source_column']} IS NOT NULL")
                        column_data = [row[0] for row in cursor.fetchall()]
                        conn.close()
                        
                        # Generate categories
                        suggested_categories = generate_categories_ai(
                            column_data, 
                            proc['source_column_description'],
                            proc['max_categories']
                        )
                        proc['categories'] = suggested_categories
                        st.rerun()
            
            # Display generated categories
            if proc.get('categories'):
                st.write("**Generated Categories:**")
                selected_categories = st.multiselect(
                    "Select categories to use:",
                    proc['categories'],
                    default=proc['categories'],
                    key=f"sel_cat_{i}"
                )
                proc['categories'] = selected_categories
                
        elif proc['type'] == 'Enrich':
            # Additional columns
            other_columns = [c[0] for c in columns if c[0] != proc['source_column']] if columns else []
            if other_columns:
                proc['additional_columns'] = st.multiselect(
                    f"Additional columns for enrichment (optional) #{i+1}",
                    other_columns,
                    default=proc['additional_columns'],
                    key=f"additional_{i}"
                )
            
            proc['expected_output'] = st.text_area(
                "What data do you want to enrich? (Describe expected output)",
                value=proc['expected_output'],
                placeholder="e.g., Return the capital city of the country",
                key=f"output_{i}"
            )
        
        # Remove process button
        if st.button(f"🗑️ Remove Process #{i+1}", key=f"remove_{i}"):
            st.session_state.processes.pop(i)
            st.rerun()

st.markdown("---")

# ===================================================================
# Step 3: Save and Run
# ===================================================================
st.header("💾 Step 3: Save Project")

if st.button("💾 Save Project"):
    if not project_name:
        st.error("❌ Project Name is required!")
    elif not table_name:
        st.error("❌ Table Name is required!")
    elif not st.session_state.processes:
        st.error("❌ At least one process is required!")
    else:
        # Save project
        project_id = save_project_to_db(server_name, database_name, project_name, project_description, table_name)
        
        if project_id:
            st.success(f"✅ Project saved with ID: {project_id}")
            
            # Save processes
            for proc in st.session_state.processes:
                if not proc['source_column'] or not proc['task_description'] or not proc['expected_output']:
                    st.warning(f"⚠️ Skipping incomplete process")
                    continue
                
                process_id = save_process_to_db(
                    server_name, database_name, project_id,
                    proc['type'], proc['task_description'],
                    proc['source_column'], proc['source_column_description'],
                    proc['additional_columns'], proc['expected_output'],
                    proc['max_categories'] if proc['type'] == 'Categorize' else None
                )
                
                if process_id and proc['type'] == 'Categorize' and proc.get('categories'):
                    save_categories_to_db(server_name, database_name, process_id, proc['categories'])
            
            st.balloons()
            st.info("🎉 Project saved successfully! You can now run the AI processor.")
            
            # Clear session
            st.session_state.processes = []
            st.session_state.project_id = project_id
        else:
            st.error("❌ Failed to save project!")

# ===================================================================
# Footer
# ===================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>AI Data Enrichment Tool v1.0 | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
