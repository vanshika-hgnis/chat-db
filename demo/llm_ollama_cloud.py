# llm_ollama_cloud.py
import os
from ollama import Client
from dotenv import load_dotenv
from rag_index import retrieve_schema_snippets

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY") or os.getenv("OLLAMA_CLOUD_KEY")

if not OLLAMA_API_KEY:
    raise ValueError("OLLAMA_API_KEY / OLLAMA_CLOUD_KEY not found in .env file.")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"},
)

MODEL = "gpt-oss:120b-cloud"  # or any other cloud model you have


def call_ollama(prompt: str) -> str:
    response = client.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


def nl_to_sql(question: str) -> str:
    # RAG: get relevant schema descriptions
    snippets = retrieve_schema_snippets(question, top_k=5)
    schema_context = "\n\n".join(snippets)

    prompt = f"""
You are an expert SQL generator for Microsoft SQL Server.

Use ONLY the schema information provided below.

SCHEMA CONTEXT:
{schema_context}

TASK:
- Generate a single safe SELECT SQL query that answers the user's question.
- Use correct table and column names from the schema context.
- Do NOT invent tables or columns.
- Do NOT use UPDATE/DELETE/INSERT/MERGE.
- Do NOT add explanations or comments.
- Only output the SQL query.

USER QUESTION:
{question}

SQL:
"""
    sql = call_ollama(prompt).strip()

    # occasionally models wrap in ```sql ... ```
    if sql.startswith("```"):
        sql = sql.strip("`")
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()
    return sql


def create_report(question: str, data):
    prompt = f"""
You are a reporting assistant.

Write a clear, concise business-style report answering the user's question
based on the provided data.

- Explain key trends and numbers.
- Avoid SQL or technical jargon.
- Use short paragraphs or bullet points.

USER QUESTION:
{question}

DATA:
{data}

REPORT:
"""
    return call_ollama(prompt)
