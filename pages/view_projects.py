"""
View Projects Page
"""

import streamlit as st
from pages.db_utils import connect_to_database, get_projects, get_processes, get_categories


def show():
    """Show the view projects page"""
    
    st.header("📊 Existing Projects")
    
    # Database connection
    st.sidebar.header("🔌 Database Connection")
    server_name = st.sidebar.text_input("Server Name", value=".")
    database_name = st.sidebar.text_input("Database Name", value="HACKATHON2026")
    
    if st.sidebar.button("🔗 Test Connection"):
        conn = connect_to_database(server_name, database_name)
        if conn:
            st.sidebar.success("✅ Connection successful!")
            conn.close()
        else:
            st.sidebar.error("❌ Connection failed")
    
    # Get projects
    projects = get_projects(server_name, database_name)
    
    if not projects:
        st.info("No projects found. Create your first project!")
    else:
        for proj in projects:
            with st.expander(f"📁 {proj[1]} (ID: {proj[0]})"):
                st.write(f"**Table:** {proj[2]}")
                st.write(f"**Description:** {proj[3] or 'N/A'}")
                st.write(f"**Created:** {proj[4]}")
                st.write(f"**Status:** {proj[5]}")
                
                # Show processes
                processes = get_processes(server_name, database_name, proj[0])
                if processes:
                    st.write("**Processes:**")
                    for proc in processes:
                        st.write(f"  - **{proc[1]}**: {proc[2]}")
                        st.write(f"    Source: {proc[3]}")
                        st.write(f"    Expected: {proc[6]}")
                        
                        if proc[1] == 'Categorize':
                            cats = get_categories(server_name, database_name, proc[0])
                            if cats:
                                st.write(f"    Categories: {', '.join(cats)}")
