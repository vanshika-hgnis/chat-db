# chat-db

Application for chatting with Database (primarily mssql through sql server) also includes an intent log which displays data table and visualization whenever necessary.

Rebuild schema + index:
'''
python schema_scanner.py
python -c "from rag_index import build_index; build_index()"
'''

Run Streamlit:
'''
streamlit run app.py
'''

After you’ve run schema_scanner.py and have connectivity to DB:
'''
python -c "from join_graph import build_join_graph; build_join_graph()"
'''

This creates: data/join_graph.json.

# Functionalities i want

✔️ Auto SQL repair loop
✔️ JOIN-inference engine - Done
✔️ Generating Python/Pandas from queries
✔️ Add schema visualization page
I can extend chart generator to:

✔ Support heatmaps
✔ Correlation matrix for numeric-heavy data
✔ Auto-detect time-series gaps
✔ Suggest best chart based on statistical distribution
✔ Let LLM choose chart type

User Question
↓
Generate SQL (LLM)
↓
Validate SQL (tables, columns, safety)
↓
Execute SQL
↓
❌ Error?
├─ Yes → Repair Prompt → New SQL → Retry (max N)
└─ No → Accept → Continue
