# services/sql_validator.py
import re
import json
from pathlib import Path

SCHEMA_FILE = Path("demo/data/db_schema.json")


def load_schema():
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_tables(sql: str):
    return re.findall(r"(?:FROM|JOIN)\s+([\w\.\[\]]+)", sql, re.IGNORECASE)


def extract_columns(sql: str):
    return re.findall(r"SELECT\s+(.*?)\s+FROM", sql, re.IGNORECASE | re.DOTALL)


def validate_sql(sql: str):
    errors = []

    if not sql.strip().lower().startswith("select"):
        errors.append("Only SELECT queries are allowed.")

    forbidden = ["update ", "delete ", "insert ", "merge ", "drop ", "alter "]
    for f in forbidden:
        if f in sql.lower():
            errors.append(f"Forbidden SQL operation detected: {f.strip()}")

    schema = load_schema()
    known_tables = {f"{t['schema']}.{t['table']}".lower() for t in schema}

    for table in extract_tables(sql):
        clean = table.replace("[", "").replace("]", "").lower()
        if "." not in clean:
            clean = f"dbo.{clean}"
        if clean not in known_tables:
            errors.append(f"Unknown table: {clean}")

    return errors
