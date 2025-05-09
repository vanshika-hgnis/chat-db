import streamlit as st
from sql_server import SQLServerConnection  # Adjust import path
# import openai
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI
# openai.api_key = os.getenv("OPENAI_API_KEY")

# SQL connection setup
db = SQLServerConnection()
connected = db.connect()

st.title("💬 Chat with Your SQL Server Data")

if not connected:
    st.error("Failed to connect to SQL Server. Check logs.")
    st.stop()

# User input
user_question = st.text_input("Ask a question about your data:")

# def ask_gpt_for_sql(question):
#     """Convert a natural language question to SQL using GPT"""
#     prompt = f"""You are an assistant who converts questions into SQL queries for SQL Server 2014. 
# Here is the question: "{question}"
# Only return the SQL query as output, nothing else."""
    
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         return response.choices[0].message["content"].strip()
#     except Exception as e:
#         st.error(f"Error with OpenAI API: {e}")
#         return None



def ask_ollama_for_sql(question, model="llama3.2:1b"):
    prompt = f"""Convert the following natural language question into a SQL Server 2014 compatible SQL query. Only return the SQL query and nothing else.

Question: {question}
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        st.error(f"Error communicating with Ollama: {e}")
        return None


if user_question:
    with st.spinner("Thinking..."):
        sql_query = ask_ollama_for_sql(user_question)
        
        if sql_query:
            st.code(sql_query, language='sql')
            
            try:
                df = db.execute_query(sql_query)
                st.dataframe(df)
            except Exception as err:
                st.error(f"Error running SQL: {err}")
        else:
            st.warning("Could not generate SQL. Try rephrasing your question.")

# Close connection on shutdown
if st.button("Close Connection"):
    db.close()
    st.success("SQL Server connection closed.")
