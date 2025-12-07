import streamlit as st
from sql_server import SQLServerConnection
from schema_embedder import SchemaEmbedder
from intent_classifier import IntentClassifier
from query_generator import SQLQueryGenerator
from chat_logger import ChatLogger

st.title("🧠 ChatDB – Talk to your SQL Database")

conn = SQLServerConnection()
conn.connect()

intent_classifier = IntentClassifier()
query_generator = SQLQueryGenerator()
logger = ChatLogger()

embedder = SchemaEmbedder()
embedder.load_index()

prompt = st.text_input("Ask something about your data:")

if st.button("Run"):
    intent = intent_classifier.classify(prompt)
    relevant_schema = embedder.search(prompt)
    schema_context = "\n".join(relevant_schema)

    if intent == "data_view" or intent == "sql_query":
        sql = query_generator.generate_sql(prompt, schema_context)
        st.write(f"Generated SQL: `{sql}`")
        df = conn.execute_query(sql)
        st.dataframe(df)
    elif intent == "data_analysis":
        sql = query_generator.generate_sql(prompt, schema_context)
        df = conn.execute_query(sql)
        st.write("Data Summary:")
        st.write(df.describe())
    elif intent == "data_visualization":
        sql = query_generator.generate_sql(prompt, schema_context)
        df = conn.execute_query(sql)
        st.line_chart(df)

    logger.log(
        intent, prompt, sql, df.head().to_dict() if not df.empty else "No result"
    )
