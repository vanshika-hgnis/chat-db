# schema_scanner.py
import json
import os
from db import get_connection
from decimal import Decimal
from datetime import datetime, date, time


DATA_DIR = "data"
SCHEMA_JSON = os.path.join(DATA_DIR, "db_schema.json")


# -----------------------------------------
# Convert SQL row values → JSON-safe values
# -----------------------------------------
def safe_value(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date, time)):
        return v.isoformat()
    # Fallback: force string
    return str(v)


def scan_schema(max_sample_rows: int = 3):
    os.makedirs(DATA_DIR, exist_ok=True)

    conn = get_connection()
    cur = conn.cursor()

    # Get all tables
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

    for schema, table in tables:
        # Columns
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
            {
                "name": c[0],
                "type": c[1],
                "nullable": (c[2] == "YES"),
            }
            for c in cols
        ]

        # Sample rows (safe conversion)
        sample_rows = []
        col_names = [c[0] for c in cols]

        try:
            cur.execute(f"SELECT TOP ({max_sample_rows}) * FROM [{schema}].[{table}]")
            rows = cur.fetchall()

            for row in rows:
                row_dict = {}
                for k, v in zip(col_names, row):
                    row_dict[k] = safe_value(v)
                sample_rows.append(row_dict)

        except Exception:
            sample_rows = []

        # Schema text for RAG
        col_desc = ", ".join(
            f"{c['name']} ({c['type']}){' NULL' if c['nullable'] else ' NOT NULL'}"
            for c in columns_struct
        )
        text = f"Table [{schema}].[{table}] with columns: {col_desc}."
        if sample_rows:
            text += f" Example rows: {sample_rows[:max_sample_rows]}"

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

    print(f"Schema saved to {SCHEMA_JSON} ({len(schema_info)} tables).")
    return schema_info


if __name__ == "__main__":
    scan_schema()
