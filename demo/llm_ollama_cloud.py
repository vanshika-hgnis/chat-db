import os
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_CLOUD_KEY")

if not OLLAMA_API_KEY:
    raise ValueError("OLLAMA_API_KEY not found in .env file.")

client = Client(
    host="https://ollama.com", headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"}
)

MODEL = "gpt-oss:120b-cloud"  # or another cloud model


def call_ollama(prompt):
    response = client.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


def nl_to_sql(question, table_schema):
    prompt = f"""
Generate a safe SELECT SQL query.
No explanation. Only SQL.

Schema:
{table_schema}

Question:
{question}

SQL:
"""
    return call_ollama(prompt).strip()


def create_report(question, data):
    prompt = f"""
Create a business-style report.

Question:
{question}

Data:
{data}

Report:
"""
    return call_ollama(prompt)
