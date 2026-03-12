"""
Project Management Page
=======================
Two modes:
1. Create New Project - define project name, table, description
2. Add Process - select existing project and add processes with categories
"""

# import streamlit as st
# from pages.db_utils import (
#     connect_to_database, get_tables, get_columns, get_projects,
#     save_project_to_db, save_process_to_db, save_categories_to_db
# )
# from pages import generate_categories_ai


# def show():
#     """Show the project management page"""
    
#     # Database connection (sidebar)
#     st.sidebar.header("🔌 Database Connection")
#     server_name = st.sidebar.text_input("Server Name", value=".")
#     database_name = st.sidebar.text_input("Database Name", value="HACKATHON2026")
    
#     # Test connection
#     if st.sidebar.button("🔗 Test Connection"):
#         conn = connect_to_database(server_name, database_name)
#         if conn:
#             st.sidebar.success("✅ Connection successful!")
#             conn.close()
#         else:
#             st.sidebar.error("❌ Connection failed")
    
#     # Main UI - Two tabs
#     st.header("📋 Project Management")
    
#     tab1, tab2 = st.tabs(["📝 Create New Project", "➕ Add Process to Project"])
    
#     # ========== TAB 1: Create New Project ==========
#     with tab1:
#         st.subheader("Create a New Project")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             new_project_name = st.text_input("Project Name *", placeholder="e.g., Job Classification", key="new_proj_name")
        
#         with col2:
#             new_table_name = st.text_input("Target Table Name *", placeholder="e.g., Employees", key="new_table_name")
        
#         new_description = st.text_area("Description (Optional)", key="new_desc")
        
#         if st.button("➕ Add Project", key="btn_add_project"):
#             if not new_project_name:
#                 st.error("❌ Project Name is required!")
#             elif not new_table_name:
#                 st.error("❌ Table Name is required!")
#             else:
#                 project_id = save_project_to_db(server_name, database_name, new_project_name, new_description, new_table_name)
#                 if project_id:
#                     st.success(f"✅ Project '{new_project_name}' created with ID: {project_id}")
#                 else:
#                     st.error("❌ Failed to create project!")
    
#     # ========== TAB 2: Add Process to Existing Project ==========
#     with tab2:
#         st.subheader("Add Process to Existing Project")
        
#         # Get existing projects
#         projects = get_projects(server_name, database_name)
        
#         if not projects:
#             st.info("ℹ️ No projects found. Create a project first in the 'Create New Project' tab.")
#         else:
#             # Project selector
#             project_options = {p[1]: p[0] for p in projects}  # {name: id}
#             selected_project_name = st.selectbox("Select Project *", list(project_options.keys()))
#             selected_project_id = project_options[selected_project_name]
            
#             # Get project details
#             selected_project = next((p for p in projects if p[0] == selected_project_id), None)
#             if selected_project:
#                 st.caption(f"📋 Table: {selected_project[2]} | Description: {selected_project[3] or 'N/A'}")
                
#                 # Get columns from the project's table
#                 table_name = selected_project[2]
#                 columns = get_columns(server_name, database_name, table_name)
                
#                 if columns:
#                     column_options = [c[0] for c in columns]
                    
#                     st.markdown("---")
#                     st.subheader("⚙️ Define Process")
                    
#                     # Process type
#                     process_type = st.selectbox("Process Type *", ["Categorize", "Enrich"], key="proc_type")
                    
#                     # Source column
#                     source_column = st.selectbox("Source Column *", column_options, key="src_col")
                    
#                     # Source column description (optional)
#                     source_column_description = st.text_input("Column Description (Optional)", key="src_desc")
                    
#                     # Destination column (for Categorize)
#                     dest_column_name = st.text_input(
#                         "Destination Column Name *", 
#                         value="ai_category",
#                         placeholder="e.g., ai_genre, ai_classification",
#                         key="dest_col"
#                     )
                    
#                     # Additional columns (optional)
#                     other_columns = [c[0] for c in columns if c[0] != source_column]
#                     additional_columns = st.multiselect("Additional Columns (Optional)", other_columns, key="add_cols")
                    
#                     if process_type == "Categorize":
#                         # Task description
#                         task_description = st.text_input(
#                             "Task Description", 
#                             placeholder="e.g., Classify jobs into categories",
#                             key="task_desc"
#                         )
                        
#                         # Expected output
#                         expected_output = st.text_input(
#                             "Expected Categories (comma-separated)",
#                             placeholder="e.g., Developer, Manager, Designer",
#                             key="exp_out"
#                         )
                        
#                         # Max categories
#                         max_categories = st.number_input("Max Categories", min_value=2, max_value=50, value=10, key="max_cat")
                        
#                         # Generate categories button
#                         can_generate = (
#                             selected_project_name and 
#                             source_column and 
#                             dest_column_name
#                         )
                        
#                         if st.button("🎯 Generate Categories", key="gen_cat", disabled=not can_generate):
#                             if can_generate:
#                                 with st.spinner("Generating categories with AI..."):
#                                     suggested = generate_categories_ai(
#                                         subject=selected_project_name,
#                                         limit=max_categories,
#                                         column_name=source_column,
#                                         dest_column_name=dest_column_name,
#                                         task_added_info=task_description
#                                     )
#                                     st.session_state['generated_categories'] = suggested
                        
#                         # Show generated categories
#                         if 'generated_categories' in st.session_state:
#                             st.write("**Generated Categories:**")
#                             selected_categories = st.multiselect(
#                                 "Select Categories to Save:",
#                                 st.session_state['generated_categories'],
#                                 default=st.session_state['generated_categories'],
#                                 key="sel_cat"
#                             )
                            
#                             # Save Process and Categories button
#                             if st.button("💾 Save Process & Categories", key="btn_save_proc"):
#                                 if not source_column:
#                                     st.error("❌ Source Column is required!")
#                                 else:
#                                     # Save process
#                                     process_id = save_process_to_db(
#                                         server_name, database_name, selected_project_id,
#                                         process_type, task_description,
#                                         source_column, source_column_description,
#                                         dest_column_name, additional_columns,
#                                         expected_output, max_categories
#                                     )
                                    
#                                     if process_id:
#                                         # Save categories
#                                         if selected_categories:
#                                             save_categories_to_db(server_name, database_name, process_id, selected_categories)
#                                             st.success(f"✅ Process saved! {len(selected_categories)} categories saved to database.")
#                                         else:
#                                             st.success(f"✅ Process saved! (No categories selected)")
                                        
#                                         # Clear generated categories
#                                         if 'generated_categories' in st.session_state:
#                                             del st.session_state['generated_categories']
#                                     else:
#                                         st.error("❌ Failed to save process!")
                    
#                     elif process_type == "Enrich":
#                         # Task description
#                         task_description = st.text_input(
#                             "Task Description", 
#                             placeholder="e.g., Enrich with company info",
#                             key="task_desc_enrich"
#                         )
                        
#                         # Expected output description
#                         expected_output = st.text_area(
#                             "What data to enrich?",
#                             placeholder="e.g., Return the company CEO name based on the company column",
#                             key="exp_out_enrich"
#                         )
                        
#                         # Save Process button
#                         if st.button("💾 Save Process", key="btn_save_enrich"):
#                             if not source_column:
#                                 st.error("❌ Source Column is required!")
#                             else:
#                                 process_id = save_process_to_db(
#                                     server_name, database_name, selected_project_id,
#                                     process_type, task_description,
#                                     source_column, source_column_description,
#                                     dest_column_name, additional_columns,
#                                     expected_output, None
#                                 )
                                
#                                 if process_id:
#                                     st.success(f"✅ Process saved!")
#                                 else:
#                                     st.error("❌ Failed to save process!")
#                 else:
#                     st.warning(f"⚠️ Could not find columns in table '{table_name}'")

"""
Project Management Page
=======================
Two modes:
1. Create New Project - define project name, table, description
2. Add Process - select existing project and add processes with categories
"""

import streamlit as st
from pages.db_utils import (
    connect_to_database, get_tables, get_columns, get_projects,
    save_project_to_db, save_process_to_db, save_categories_to_db
)
from pages import generate_categories_ai


def show():
    """Show the project management page"""
    
    # Database connection (sidebar)
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
    
    # Main UI - Two tabs
    st.header("📋 Project Management")
    
    tab1, tab2 = st.tabs(["📝 Create New Project", "➕ Add Process to Project"])
    
    # ========== TAB 1: Create New Project ==========
    with tab1:
        st.subheader("Create a New Project")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_project_name = st.text_input(
                "Project Name *",
                placeholder="e.g., Job Classification",
                key="new_proj_name"
            )
        
        with col2:
            new_table_name = st.text_input(
                "Target Table Name *",
                placeholder="e.g., Employees",
                key="new_table_name"
            )
        
        new_description = st.text_area("Description (Optional)", key="new_desc")
        
        if st.button("➕ Add Project", key="btn_add_project"):
            if not new_project_name:
                st.error("❌ Project Name is required!")
            elif not new_table_name:
                st.error("❌ Table Name is required!")
            else:
                project_id = save_project_to_db(
                    server_name,
                    database_name,
                    new_project_name,
                    new_description,
                    new_table_name
                )
                
                if project_id:
                    st.success(f"✅ Project '{new_project_name}' created with ID: {project_id}")
                else:
                    st.error("❌ Failed to create project!")
    
    # ========== TAB 2: Add Process to Existing Project ==========
    with tab2:
        st.subheader("Add Process to Existing Project")
        
        projects = get_projects(server_name, database_name)
        
        if not projects:
            st.info("ℹ️ No projects found. Create a project first in the 'Create New Project' tab.")
        else:
            
            project_options = {p[1]: p[0] for p in projects}
            
            selected_project_name = st.selectbox(
                "Select Project *",
                list(project_options.keys())
            )
            
            selected_project_id = project_options[selected_project_name]
            
            selected_project = next(
                (p for p in projects if p[0] == selected_project_id),
                None
            )
            
            if selected_project:
                
                st.caption(
                    f"📋 Table: {selected_project[2]} | Description: {selected_project[3] or 'N/A'}"
                )
                
                table_name = selected_project[2]
                
                columns = get_columns(server_name, database_name, table_name)
                
                if columns:
                    
                    column_options = [c[0] for c in columns]
                    
                    st.markdown("---")
                    st.subheader("⚙️ Define Process")
                    
                    process_type = st.selectbox(
                        "Process Type *",
                        ["Categorize", "Enrich"],
                        key="proc_type"
                    )
                    
                    source_column = st.selectbox(
                        "Source Column *",
                        column_options,
                        key="src_col"
                    )
                    
                    source_column_description = st.text_input(
                        "Column Description (Optional)",
                        key="src_desc"
                    )
                    
                    # Destination column (choose from ai_ columns)
                    ai_columns = [c for c in column_options if c.startswith("ai_")]
                    
                    if ai_columns:
                        dest_column_name = st.selectbox(
                            "Destination Column *",
                            ai_columns,
                            key="dest_col"
                        )
                    else:
                        st.warning("⚠️ No columns starting with 'ai_' found in this table.")
                        dest_column_name = st.text_input(
                            "Destination Column Name *",
                            value="ai_category",
                            key="dest_col_fallback"
                        )
                    
                    other_columns = [c[0] for c in columns if c[0] != source_column]
                    
                    additional_columns = st.multiselect(
                        "Additional Columns (Optional)",
                        other_columns,
                        key="add_cols"
                    )
                    
                    if process_type == "Categorize":
                        
                        task_description = st.text_input(
                            "Task Description",
                            placeholder="e.g., Classify jobs into categories",
                            key="task_desc"
                        )
                        
                        max_categories = st.number_input(
                            "Max Categories",
                            min_value=2,
                            max_value=50,
                            value=10,
                            key="max_cat"
                        )
                        
                        can_generate = (
                            selected_project_name
                            and source_column
                            and dest_column_name
                        )
                        
                        if st.button(
                            "🎯 Generate Categories",
                            key="gen_cat",
                            disabled=not can_generate
                        ):
                            
                            if can_generate:
                                
                                with st.spinner("Generating categories with AI..."):
                                    
                                    suggested = generate_categories_ai(
                                        subject=selected_project_name,
                                        limit=max_categories,
                                        column_name=source_column,
                                        dest_column_name=dest_column_name,
                                        task_added_info=task_description
                                    )
                                    
                                    st.session_state['generated_categories'] = suggested
                    
                    # ==============================
                    # SHOW GENERATED CATEGORIES
                    # ==============================
                    
                    if 'generated_categories' in st.session_state:
                        
                        st.write("**Generated Categories:**")
                        
                        extra_categories_text = st.text_input(
                            "Add additional categories (comma-separated)",
                            placeholder="e.g., Analyst, Researcher",
                            key="extra_cat"
                        )
                        
                        extra_categories = []
                        
                        if extra_categories_text:
                            extra_categories = [
                                c.strip()
                                for c in extra_categories_text.split(",")
                                if c.strip()
                            ]
                        
                        selected_categories = st.multiselect(
                            "Select Categories to Save:",
                            st.session_state['generated_categories'],
                            default=st.session_state['generated_categories'],
                            key="sel_cat"
                        )
                        
                        if st.button("💾 Save Process & Categories", key="btn_save_proc"):
                            
                            if not source_column:
                                st.error("❌ Source Column is required!")
                            
                            else:
                                
                                process_id = save_process_to_db(
                                    server_name,
                                    database_name,
                                    selected_project_id,
                                    process_type,
                                    task_description,
                                    source_column,
                                    source_column_description,
                                    dest_column_name,
                                    additional_columns,
                                    max_categories
                                )
                                
                                if process_id:
                                    
                                    final_categories = list(
                                        set(selected_categories + extra_categories)
                                    )
                                    
                                    if final_categories:
                                        
                                        save_categories_to_db(
                                            server_name,
                                            database_name,
                                            process_id,
                                            final_categories
                                        )
                                        
                                        st.success(
                                            f"✅ Process saved! {len(final_categories)} categories saved to database."
                                        )
                                    
                                    else:
                                        st.success("✅ Process saved! (No categories selected)")
                                    
                                    if 'generated_categories' in st.session_state:
                                        del st.session_state['generated_categories']
                                
                                else:
                                    st.error("❌ Failed to save process!")
                    
                    elif process_type == "Enrich":
                        
                        task_description = st.text_input(
                            "Task Description",
                            placeholder="e.g., Enrich with company info",
                            key="task_desc_enrich"
                        )
                        
                        expected_output = st.text_area(
                            "What data to enrich?",
                            placeholder="e.g., Return the company CEO name based on the company column",
                            key="exp_out_enrich"
                        )
                        
                        if st.button("💾 Save Process", key="btn_save_enrich"):
                            
                            if not source_column:
                                st.error("❌ Source Column is required!")
                            
                            else:
                                
                                process_id = save_process_to_db(
                                    server_name,
                                    database_name,
                                    selected_project_id,
                                    process_type,
                                    task_description,
                                    source_column,
                                    source_column_description,
                                    dest_column_name,
                                    additional_columns,
                                    None
                                )
                                
                                if process_id:
                                    st.success("✅ Process saved!")
                                else:
                                    st.error("❌ Failed to save process!")
                
                else:
                    st.warning(f"⚠️ Could not find columns in table '{table_name}'")