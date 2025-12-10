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
✔️ JOIN-inference engine
✔️ Generating Python/Pandas from queries
✔️ Add schema visualization page
