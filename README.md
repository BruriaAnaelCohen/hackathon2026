# AI Data Enrichment Tool

## Overview

This tool enables **BI Developers** to enrich their data using AI directly from an intuitive **Streamlit GUI**. It leverages **Ollama** (local LLM) to categorize data without requiring external API keys or paid services.

## The Problem

BI developers often need to:
- Classify/categorize text data (e.g., job titles, product categories, customer segments)
- Enrich data with AI-generated insights
- Automate repetitive categorization tasks

**Traditional solutions** require:
- Writing complex SQL or Python scripts
- Setting up external API integrations
- Handling rate limits and costs

**Our solution**: A simple GUI where developers define their categorization tasks, generate AI-powered categories, and run them as part of their ETL pipeline.

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit App (GUI)                      │
│  - Project Management (create projects, add processes)      │
│  - Generate AI categories                                   │
│  - View projects and processes                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   SQL Server Database                       │
│  - AI_Projects: stores project definitions                   │
│  - AI_Processes: stores process configs                    │
│  - AI_Categories: stores category lists                    │
│  - Your Data Tables: enriched with AI results              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              activate_process.py (ETL Script)                │
│  - Runs as part of your ETL pipeline                       │
│  - Takes table_name + dest_column as arguments             │
│  - Processes rows using AI (Ollama)                        │
│  - Updates destination column in your table                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Ollama                                │
│  - Local LLM server (mistral, llama3, etc.)               │
│  - No API costs                                            │
│  - Runs on localhost:11434                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### AI_Projects
| Column | Type | Description |
|--------|------|-------------|
| ProjectID | INT | Primary key (auto-increment) |
| ProjectName | NVARCHAR | Name of the project |
| ServerName | NVARCHAR | SQL Server name |
| DatabaseName | NVARCHAR | Database name |
| TableName | NVARCHAR | Target table to process |
| Description | NVARCHAR | Optional description |
| CreatedDate | DATETIME | Creation timestamp |
| Status | NVARCHAR | Project status (Active, etc.) |

### AI_Processes
| Column | Type | Description |
|--------|------|-------------|
| ProcessID | INT | Primary key |
| ProjectID | INT | Foreign key to AI_Projects |
| ProcessType | NVARCHAR | "Categorize" (Enrich planned) |
| TaskDescription | NVARCHAR | Description of the task |
| SourceColumn | NVARCHAR | Column containing data to process |
| SourceColumnDescription | NVARCHAR | Optional column description |
| DestColumn | NVARCHAR | Column to store AI result |
| AdditionalColumns | NVARCHAR | JSON - extra columns for AI context |
| ExpectedOutput | NVARCHAR | Expected categories (for reference) |
| MaxCategories | INT | Max categories to generate |
| CreatedDate | DATETIME | Creation timestamp |

### AI_Categories
| Column | Type | Description |
|--------|------|-------------|
| CategoryID | INT | Primary key |
| ProcessID | INT | Foreign key to AI_Processes |
| CategoryName | NVARCHAR | The category name |

---

## Workflow

### Step 1: Define a Project (Streamlit GUI)

1. Open the Streamlit app: `streamlit run streamlit_app.py`
2. Go to **Project Management** → **Create New Project**
3. Enter:
   - **Project Name**: e.g., "Employee Classification"
   - **Table Name**: e.g., "Employees"
   - **Description**: Optional

4. Click **Add Project**

### Step 2: Add a Categorize Process

1. Go to **Add Process to Project** tab
2. Select your project from the dropdown
3. Configure:
   - **Process Type**: Categorize
   - **Source Column**: The column containing data to categorize (e.g., "JobTitle")
   - **Destination Column**: Where to store the result (e.g., "ai_category")
   - **Max Categories**: Number of categories to generate

4. Click **Generate Categories** - this calls Ollama to suggest categories based on your data

5. Select the categories you want to use

6. Click **Save Process & Categories**

### Step 3: Run the ETL (activate_process.py)

The actual processing runs as part of your ETL pipeline:

```bash
python pages/activate_process.py <table_name> <dest_column>
```

Example:
```bash
python pages/activate_process.py Employees ai_category
```

This will:
1. Find the process for table "Employees" with dest column "ai_category"
2. Load the saved categories from the database
3. Loop through all rows where `ai_category` is NULL
4. For each row, call Ollama to categorize the JobTitle
5. Update the `ai_category` column

---

## Files Overview

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main Streamlit application |
| `pages/create_project.py` | Project & process management UI |
| `pages/view_projects.py` | View existing projects |
| `pages/db_utils.py` | Database operations |
| `pages/ai_utils.py` | AI category generation (calls Ollama) |
| `pages/activate_process.py` | ETL script - processes rows with AI |
| `sql/metadata_setup.sql` | Database schema creation |

---

## Categorize Feature Explained

### How AI Categories Work

1. **Generation**: When you click "Generate Categories", the system sends a prompt to Ollama:
   ```
   Generate 10 categories for classifying job titles.
   Source column: JobTitle
   Subject: Employees
   ```

2. **Selection**: You select which categories to keep

3. **Processing**: When `activate_process.py` runs, for each row:
   ```
   Categorize "Senior Software Engineer" into ONE of:
   Developer, Manager, Designer, Analyst, Executive
   
   Respond ONLY with the category name.
   ```

4. **Result**: The database is updated:
   ```sql
   UPDATE Employees SET ai_category = 'Developer' WHERE EmployeeID = 1
   ```

---

## Requirements

- **Python 3.8+**
- **Streamlit**: `pip install streamlit`
- **PyODBC**: `pip install pyodbc`
- **Ollama**: Download from https://ollama.ai
  - Run: `ollama serve`
  - Pull model: `ollama pull llama3` (or `mistral`)

---

## Quick Start

### 1. Setup Database

Run the SQL script to create metadata tables:
```sql
-- In SQL Server Management Studio
sqlcmd -S . -d HACKATHON2026 -i sql/metadata_setup.sql
```

### 2. Start Ollama

```bash
ollama serve
ollama pull llama3
```

### 3. Run Streamlit

```bash
cd hackathon2026
streamlit run streamlit_app.py
```

### 4. Create a Project

1. Create project: "Books", Table: "Books"
2. Add process: Source="BookName", Dest="ai_genre"
3. Generate categories: "Fiction, Science Fiction, Mystery, Romance, Biography"
4. Save

### 5. Run ETL

```bash
python pages/activate_process.py Books ai_genre
```

---

## Notes

- **Enrich feature** is not implemented (not planned in near future)
- Uses **ROW_NUMBER()** to identify rows (no primary key needed in script)
- All processing uses **Ollama** (local, free, no API keys)
- The ETL script is designed to be called from your existing ETL pipeline
