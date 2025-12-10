# schema_scanner.py
import json
import os
from db import get_connection
from decimal import Decimal
from datetime import datetime, date, time

DATA_DIR = "data"
SCHEMA_JSON = os.path.join(DATA_DIR, "db_schema.json")
TABLE_LIST_TXT = os.path.join(DATA_DIR, "table_list.txt")


def safe_value(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date, time)):
        return v.isoformat()
    return str(v)


def scan_schema(max_sample_rows: int = 3):
    os.makedirs(DATA_DIR, exist_ok=True)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    )
    tables = cur.fetchall()

    schema_info = []
    table_list = []

    for schema, table in tables:
        table_list.append(f"{schema}.{table}")

        cur.execute(
            """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """,
            (schema, table),
        )
        cols = cur.fetchall()

        columns_struct = [
            {"name": c[0], "type": c[1], "nullable": (c[2] == "YES")} for c in cols
        ]

        col_names = [c[0] for c in cols]
        sample_rows = []

        try:
            cur.execute(f"SELECT TOP ({max_sample_rows}) * FROM [{schema}].[{table}]")
            rows = cur.fetchall()
            for row in rows:
                safe_row = {}
                for k, v in zip(col_names, row):
                    safe_row[k] = safe_value(v)
                sample_rows.append(safe_row)
        except:
            pass

        col_text = ", ".join(
            f"{c['name']} ({c['type']}){' NULL' if c['nullable'] else ''}"
            for c in columns_struct
        )

        text = f"Table [{schema}].[{table}] columns: {col_text}."
        if table.lower() in ["allowance", "allowances"]:
            text = "This table stores allowance configuration. " + text
        if sample_rows:
            text += f" Example rows: {sample_rows}"

        schema_info.append(
            {
                "schema": schema,
                "table": table,
                "columns": columns_struct,
                "sample_rows": sample_rows,
                "text": text,
            }
        )

    conn.close()

    with open(SCHEMA_JSON, "w", encoding="utf-8") as f:
        json.dump(schema_info, f, ensure_ascii=False, indent=2)

    with open(TABLE_LIST_TXT, "w", encoding="utf-8") as f:
        for t in table_list:
            f.write(t + "\n")

    print("Schema extracted successfully.")
    print(f"- Tables: {len(table_list)}")
    print(f"- Saved: {SCHEMA_JSON}, {TABLE_LIST_TXT}")


if __name__ == "__main__":
    scan_schema()
