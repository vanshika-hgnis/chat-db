import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:latest"  # small model, fits in low RAM


def call_llm(prompt):
    payload = {"model": MODEL, "prompt": prompt, "stream": False}

    resp = requests.post(OLLAMA_URL, json=payload)
    resp.raise_for_status()

    data = resp.json()
    return data.get("response", "")


def nl_to_sql(question, table_schema):
    prompt = f"""
You are an SQL generator. Convert the question into a safe SELECT SQL query.
ONLY output SQL. Do not explain.
Use the exact schema.

Schema:
{table_schema}

Question: {question}

SQL:
"""
    return call_llm(prompt).strip()


def create_report(question, data):
    prompt = f"""
Create a clear and short business-style report.

Question: {question}

Data:
{data}

Report:
"""
    return call_llm(prompt)
