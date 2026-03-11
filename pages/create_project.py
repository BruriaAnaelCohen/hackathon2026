"""
Create Project Page
"""

import streamlit as st
from pages.db_utils import (
    connect_to_database, get_tables, get_columns,
    save_project_to_db, save_process_to_db, save_categories_to_db
)
from pages import generate_categories_ai


def show():
    """Show the create project page"""
    
    # Session state for processes
    if 'processes' not in st.session_state:
        st.session_state.processes = []
    
    # Database connection
    st.sidebar.header("🔌 Database Connection")
    server_name = st.sidebar.text_input("Server Name", value=".")
    database_name = st.sidebar.text_input("Database Name", value="HACKATHON2026")
    
    # Test connection
    if st.sidebar.button("🔗 Test Connection"):
        conn = connect_to_database(server_name, database_name)
        if conn:
            st.sidebar.success("✅ Connection successful!")
            conn.close()
        else:
            st.sidebar.error("❌ Connection failed")
    
    # Step 1: Project Setup
    st.header("📝 Step 1: Create New Project")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("Project Name *", placeholder="e.g., Job Classification")
    
    with col2:
        table_name = st.text_input("Target Table Name *", placeholder="e.g., Employees")
    
    project_description = st.text_area("Description (Optional)")
    
    # Get columns
    columns = []
    if table_name:
        columns = get_columns(server_name, database_name, table_name)
        if columns:
            st.success(f"✅ Found {len(columns)} columns in '{table_name}'")
        else:
            st.warning(f"⚠️ Could not find columns")
    
    st.markdown("---")
    
    # Step 2: Processes
    st.header("⚙️ Step 2: Define Processes")
    
    if st.button("➕ Add Process"):
        st.session_state.processes.append({
            'type': 'Categorize',
            'task_description': '',
            'source_column': '',
            'source_column_description': '',
            'dest_column_name': 'ai_category',
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
                    f"Type #{i+1}", ['Categorize', 'Enrich'],
                    index=0 if proc['type'] == 'Categorize' else 1,
                    key=f"type_{i}"
                )
            
            with col2:
                if columns:
                    column_options = [c[0] for c in columns]
                    proc['source_column'] = st.selectbox(
                        f"Column #{i+1}", column_options,
                        index=column_options.index(proc['source_column']) if proc['source_column'] in column_options else 0,
                        key=f"source_{i}"
                    )
            
            proc['task_description'] = st.text_area(
                f"Task Description #{i+1}",
                value=proc['task_description'],
                placeholder="e.g., Classify jobs into categories",
                key=f"task_{i}"
            )
            
            proc['source_column_description'] = st.text_input(
                f"Column Description (Optional) #{i+1}",
                value=proc['source_column_description'],
                key=f"desc_{i}"
            )
            
            if proc['type'] == 'Categorize':
                other_columns = [c[0] for c in columns if c[0] != proc['source_column']] if columns else []
                if other_columns:
                    proc['additional_columns'] = st.multiselect(
                        f"Additional columns #{i+1}", other_columns,
                        default=proc['additional_columns'],
                        key=f"additional_{i}"
                    )
                
                proc['expected_output'] = st.text_input(
                    "Expected categories (word or phrase)",
                    value=proc['expected_output'],
                    placeholder="e.g., Cleaner, Programmer, Manager",
                    key=f"output_{i}"
                )
                
                proc['dest_column_name'] = st.text_input(
                    "Destination column name (where to save categories)",
                    value=proc.get('dest_column_name', 'ai_category'),
                    placeholder="e.g., ai_category, ai_genre",
                    key=f"dest_{i}"
                )
                
                proc['max_categories'] = st.number_input(
                    "Max categories", min_value=2, max_value=50,
                    value=proc['max_categories'],
                    key=f"max_{i}"
                )
                
                # Generate categories button - only enabled when required fields are filled
                can_generate = (
                    project_name and 
                    proc['source_column'] and 
                    proc['dest_column_name'] and
                    table_name
                )
                
                if st.button(f"🎯 Generate Categories #{i+1}", key=f"gen_cat_{i}", disabled=not can_generate):
                    if can_generate:
                        suggested = generate_categories_ai(
                            subject=project_name,
                            limit=proc['max_categories'],
                            column_name=proc['source_column'],
                            dest_column_name=proc['dest_column_name']
                        )
                        proc['categories'] = suggested
                        st.rerun()
                
                if not can_generate:
                    st.caption("⚠️ Fill in Project Name, Source Column, and Destination Column to enable")
                
                if proc.get('categories'):
                    st.write("**Generated Categories:**")
                    selected = st.multiselect(
                        "Select categories:",
                        proc['categories'],
                        default=proc['categories'],
                        key=f"sel_cat_{i}"
                    )
                    proc['categories'] = selected
                    
            elif proc['type'] == 'Enrich':
                other_columns = [c[0] for c in columns if c[0] != proc['source_column']] if columns else []
                if other_columns:
                    proc['additional_columns'] = st.multiselect(
                        f"Additional columns #{i+1}", other_columns,
                        default=proc['additional_columns'],
                        key=f"additional_{i}"
                    )
                
                proc['expected_output'] = st.text_area(
                    "What data to enrich?",
                    value=proc['expected_output'],
                    placeholder="e.g., Return the capital city",
                    key=f"output_{i}"
                )
            
            if st.button(f"🗑️ Remove Process #{i+1}", key=f"remove_{i}"):
                st.session_state.processes.pop(i)
                st.rerun()
    
    st.markdown("---")
    
    # Step 3: Save
    st.header("💾 Step 3: Save Project")
    
    if st.button("💾 Save Project"):
        if not project_name:
            st.error("❌ Project Name is required!")
        elif not table_name:
            st.error("❌ Table Name is required!")
        elif not st.session_state.processes:
            st.error("❌ At least one process is required!")
        else:
            project_id = save_project_to_db(server_name, database_name, project_name, project_description, table_name)
            
            if project_id:
                st.success(f"✅ Project saved with ID: {project_id}")
                
                saved_count = 0
                for proc in st.session_state.processes:
                    # Only require source_column to save the process
                    if not proc['source_column']:
                        continue
                    
                    process_id = save_process_to_db(
                        server_name, database_name, project_id,
                        proc['type'], proc['task_description'],
                        proc['source_column'], proc['source_column_description'],
                        proc.get('dest_column_name', 'ai_category'),
                        proc['additional_columns'], proc['expected_output'],
                        proc['max_categories'] if proc['type'] == 'Categorize' else None
                    )
                    
                    if process_id and proc['type'] == 'Categorize' and proc.get('categories'):
                        save_categories_to_db(server_name, database_name, process_id, proc['categories'])
                        saved_count += 1
                    elif process_id:
                        saved_count += 1
                
                if saved_count > 0:
                    st.success(f"✅ Saved {saved_count} process(es) with categories!")
                else:
                    st.warning("⚠️ No processes were saved. Make sure to select a Source Column.")
                
                st.balloons()
                st.session_state.processes = []
            else:
                st.error("❌ Failed to save project!")
