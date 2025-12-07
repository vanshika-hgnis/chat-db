import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

APIKEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=APIKEY)

MODEL = "gemini-2.0-flash-lite"


def nl_to_sql(question, table_schema):
    prompt = f"""
You are an SQL generator. Convert the question into a safe SELECT SQL query.
Do NOT modify table/column names. Do NOT use update/insert/delete.
Only produce SQL. 

Schema:
{table_schema}

Question: {question}

SQL:
    """

    resp = genai.GenerativeModel(MODEL).generate_content(prompt)
    return resp.text.strip("` ")


def create_report(question, data):
    prompt = f"""
You are a reporting AI. Summarize the following data in a clear business-style report.

User Question: {question}

Data:
{data}

Write a short report:
"""

    resp = genai.GenerativeModel(MODEL).generate_content(prompt)
    return resp.text
