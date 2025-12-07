import pyodbc
import os
from dotenv import load_dotenv


SERVER = os.getenv("DB_SERVER")
NAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")


def get_connection():
    server = SERVER
    database = NAME
    username = USER
    password = PASSWORD

    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    return pyodbc.connect(conn_str)


def run_sql(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return columns, rows
