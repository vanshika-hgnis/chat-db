# services/sql_repair.py
from services.sql_validator import validate_sql
from llm_ollama_cloud import call_ollama

MAX_REPAIR_ATTEMPTS = 3


def repair_sql(original_sql: str, error_message: str):
    prompt = f"""
You are a SQL Server expert.

The following SQL query is INVALID.

SQL:
{original_sql}

ERROR:
{error_message}

RULES:
- Use only existing tables and columns
- Use SELECT only
- No explanation
- Return ONLY corrected SQL

Corrected SQL:
"""
    return call_ollama(prompt).strip()


def sql_with_auto_repair(generate_sql_fn, run_sql_fn, question: str):
    sql = generate_sql_fn(question)

    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        # 1. Static validation
        validation_errors = validate_sql(sql)
        if validation_errors:
            sql = repair_sql(sql, "; ".join(validation_errors))
            continue

        # 2. Execute SQL
        try:
            columns, rows = run_sql_fn(sql)

            # 3. Empty-result guard
            if not rows:
                sql = repair_sql(sql, "Query returned zero rows.")
                continue

            return sql, columns, rows

        except Exception as e:
            sql = repair_sql(sql, str(e))

    raise RuntimeError("SQL auto-repair failed after multiple attempts.")
