# db.py
import pyodbc
import os
from dotenv import load_dotenv

# Load .env once, at import
load_dotenv()

SERVER = os.getenv("DB_SERVER")
NAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")


def get_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER};DATABASE={NAME};UID={USER};PWD={PASSWORD}"
    )
    return pyodbc.connect(conn_str)


def run_sql(query: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return columns, rows
