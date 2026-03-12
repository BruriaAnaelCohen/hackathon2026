"""
AI Data Enrichment Tool - Main App
===================================
"""

import streamlit as st

st.set_page_config(
    page_title="AI Data Enrichment Tool",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Data Enrichment Tool")
st.markdown("---")

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Project Management", "View Projects"])

if page == "Home":
    st.markdown("""
    ## Welcome to AI Data Enrichment Tool
    
    This tool helps you:
    - Connect to your database
    - Define AI tasks (Categorize/Enrich)
    - Process data using AI models
    
    ### Getting Started
    1. Go to **Project Management** to management your project
    2. Define your processes (categorization or enrichment)
    3. Run the AI processor
    
    ### Available Scripts
    - `analyze_book_genre_ollama.py` - Process books with Ollama
    - `analyze_book_genre_arcee.py` - Process books with Arcee AI
    - `ai_processor.py` - Run by project name
    """)
    
elif page == "Project Management":
    st.markdown("## Project Management")
    st.info("Create new projects or add processes to existing projects.")
    
    # Import and run the project creation
    from pages import create_project
    create_project.show()
    
elif page == "View Projects":
    st.markdown("## View Projects")
    st.info("View existing projects and their processes.")
    
    # Import and run project viewing
    from pages import view_projects
    view_projects.show()
