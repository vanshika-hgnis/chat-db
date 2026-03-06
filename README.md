# chat-db

**chat-db** is a Streamlit application that lets you query a Microsoft SQL Server database using plain English. You type a question, and the app generates SQL using an LLM, runs it against your database, and returns the results alongside a plain-language report and an auto-selected chart.

---

## Features

- **Natural Language to SQL** – Ask questions in plain English; the LLM generates safe, read-only `SELECT` queries.
- **RAG-powered Schema Retrieval** – Relevant table/column context is retrieved via a FAISS semantic index so the LLM always works with the right schema snippets.
- **JOIN Inference Engine** – Builds a join graph from real foreign keys and heuristic column-name matching, then feeds join hints to the LLM prompt.
- **Auto SQL Repair Loop** – If the generated SQL fails, the app automatically retries with an error-aware repair prompt.
- **Smart Chart Generation** – Detects the intent of your question (trend, comparison, distribution, correlation) and picks the most appropriate chart type (line, bar, pie, scatter).
- **Business-style Reports** – Alongside the data table, the LLM writes a concise, jargon-free summary of the results.
- **Multiple LLM Backends** – Ships with Ollama Cloud as the default; Gemini and local Ollama adapters are included under `demo/Other_LLM_Providers/`.

---

## Architecture

```
User Question
     ↓
Generate SQL  ←  RAG schema snippets + JOIN hints (LLM)
     ↓
Validate SQL (tables, columns, safety)
     ↓
Execute SQL against SQL Server
     ↓
  Error?
  ├─ Yes → Repair Prompt → New SQL → Retry (max N times)
  └─ No  → Accept → Continue
     ↓
Display: Data Table + Business Report + Auto Chart
```

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | |
| Microsoft SQL Server | Any edition; ODBC Driver 17 for SQL Server must be installed |
| [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) | Required by `pyodbc` |
| Ollama Cloud account | For the default LLM backend – obtain an API key from [ollama.com](https://ollama.com) |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/vanshika-hgnis/chat-db.git
cd chat-db
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file inside the `demo/` directory (next to `app.py`):

```env
# SQL Server connection
DB_SERVER=your_server_name_or_ip
DB_NAME=your_database_name
DB_USER=your_sql_username
DB_PASSWORD=your_sql_password

# LLM – Ollama Cloud (default)
OLLAMA_API_KEY=your_ollama_cloud_api_key
```

> **Alternative LLM backends** – see `demo/Other_LLM_Providers/` for Gemini (`llm.py`, requires `GEMINI_KEY`) and local Ollama (`llm_local.py`, no API key needed). Swap the import in `app.py` to switch providers.

### 5. Scan the database schema

Run this once (and again whenever your schema changes):

```bash
cd demo
python schema_scanner.py
```

This creates:
- `data/db_schema.json` – full schema with sample rows
- `data/table_list.txt` – flat list of all tables

### 6. Build the FAISS semantic index

```bash
python -c "from rag_index import build_index; build_index()"
```

This creates `data/schema.index` and `data/schema_texts.json` used for RAG retrieval.

### 7. Build the JOIN graph

```bash
python -c "from join_graph import build_join_graph; build_join_graph()"
```

This creates `data/join_graph.json` containing foreign-key and heuristic join relationships.

> Steps 5–7 only need to be re-run when your database schema changes.

---

## Running the App

```bash
cd demo
streamlit run app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`), type a question about your database, and click **Generate Report**.

---

## Project Structure

```
chat-db/
├── demo/
│   ├── app.py                  # Streamlit entry point
│   ├── db.py                   # SQL Server connection & query runner
│   ├── schema_scanner.py       # Scans DB schema → data/db_schema.json
│   ├── rag_index.py            # Builds & queries FAISS semantic index
│   ├── join_graph.py           # JOIN inference engine
│   ├── llm_ollama_cloud.py     # Default LLM adapter (Ollama Cloud)
│   ├── chart_generator.py      # Legacy chart generator
│   ├── services/
│   │   ├── char_service.py     # Smart chart builder (intent-aware)
│   │   ├── question_intent.py  # Detects query intent (trend/compare/…)
│   │   └── semantic_engine.py  # Classifies DataFrame columns by role
│   ├── utils/
│   │   └── numeric_cleaner.py  # Cleans numeric columns in DataFrames
│   ├── Other_LLM_Providers/
│   │   ├── llm.py              # Gemini adapter
│   │   └── llm_local.py        # Local Ollama adapter
│   └── data/                   # Generated at runtime (not committed)
│       ├── db_schema.json
│       ├── schema.index
│       ├── schema_texts.json
│       └── join_graph.json
├── requirements.txt
└── .streamlit/
    └── config.toml
```

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
