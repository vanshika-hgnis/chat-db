# join_graph.py
"""
JOIN-Inference engine.

1. Reads foreign keys from SQL Server (strong joins).
2. Adds heuristic joins where tables share the same column name & type.
3. Saves everything to data/join_graph.json.
4. Exposes suggest_join_hints(question) for the LLM prompt.
"""

import os
import json
from typing import Dict, List, Tuple
from db import get_connection

DATA_DIR = "data"
JOIN_GRAPH_JSON = os.path.join(DATA_DIR, "join_graph.json")


def build_join_graph() -> Dict[str, List[dict]]:
    """
    Build join graph using:
    - Real foreign keys (sys.foreign_keys)
    - Heuristic joins on same column names

    Returns adjacency dict: { "schema.table": [edge, ...], ... }
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    conn = get_connection()
    cur = conn.cursor()

    # 1) Strong edges from FOREIGN KEYS
    cur.execute(
        """
        SELECT 
            OBJECT_SCHEMA_NAME(fk.parent_object_id) AS fk_schema,
            OBJECT_NAME(fk.parent_object_id)        AS fk_table,
            pc.name                                 AS fk_column,
            OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS pk_schema,
            OBJECT_NAME(fk.referenced_object_id)        AS pk_table,
            rc.name                                     AS pk_column
        FROM sys.foreign_keys fk
        JOIN sys.foreign_key_columns fkc
            ON fk.object_id = fkc.constraint_object_id
        JOIN sys.columns pc
            ON fkc.parent_object_id = pc.object_id
           AND fkc.parent_column_id = pc.column_id
        JOIN sys.columns rc
            ON fkc.referenced_object_id = rc.object_id
           AND fkc.referenced_column_id = rc.column_id
        WHERE fk.is_disabled = 0
    """
    )
    fk_rows = cur.fetchall()

    edges: List[dict] = []

    for row in fk_rows:
        fk_schema, fk_table, fk_col, pk_schema, pk_table, pk_col = row
        left = f"{fk_schema}.{fk_table}"
        right = f"{pk_schema}.{pk_table}"

        edges.append(
            {
                "left": left,
                "right": right,
                "left_column": fk_col,
                "right_column": pk_col,
                "source": "foreign_key",
                "score": 1.0,
            }
        )

    # 2) Heuristic edges: same column name & type in multiple tables
    cur.execute(
        """
        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
    """
    )
    cols = cur.fetchall()
    conn.close()

    by_col: Dict[str, List[Tuple[str, str]]] = {}
    for schema, table, col, dtype in cols:
        key = col.lower()
        table_name = f"{schema}.{table}"
        by_col.setdefault(key, []).append((table_name, dtype))

    generic_cols = {
        "id",
        "createddate",
        "modifieddate",
        "created_by",
        "updated_by",
        "rowversion",
        "timestamp",
    }

    for col_name, tables in by_col.items():
        if len(tables) < 2:
            continue
        if col_name in generic_cols:
            continue

        for i in range(len(tables)):
            for j in range(i + 1, len(tables)):
                t1, dt1 = tables[i]
                t2, dt2 = tables[j]
                if t1 == t2:
                    continue
                if dt1 != dt2:
                    continue  # require same datatype for heuristic edge

                edges.append(
                    {
                        "left": t1,
                        "right": t2,
                        "left_column": col_name,
                        "right_column": col_name,
                        "source": "same_column_name",
                        "score": 0.6,  # weaker than foreign key
                    }
                )

    # 3) Build adjacency graph
    graph: Dict[str, List[dict]] = {}
    for e in edges:
        graph.setdefault(e["left"], []).append(e)

        # also add reverse direction
        rev = {
            "left": e["right"],
            "right": e["left"],
            "left_column": e["right_column"],
            "right_column": e["left_column"],
            "source": e["source"],
            "score": e["score"],
        }
        graph.setdefault(rev["left"], []).append(rev)

    with open(JOIN_GRAPH_JSON, "w", encoding="utf-8") as f:
        json.dump({"edges": edges, "graph": graph}, f, ensure_ascii=False, indent=2)

    print(f"Join graph saved to {JOIN_GRAPH_JSON} with {len(edges)} edges.")
    return graph


def _load_join_graph() -> Dict[str, List[dict]]:
    if not os.path.exists(JOIN_GRAPH_JSON):
        raise FileNotFoundError(
            f"{JOIN_GRAPH_JSON} not found. Run build_join_graph() once first."
        )
    with open(JOIN_GRAPH_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["graph"]


def suggest_join_hints(question: str, max_pairs: int = 10) -> str:
    """
    Given the natural-language question, return textual join hints
    like:
      - Join dbo.sales and dbo.partymaster ON dbo.sales.pcode = dbo.partymaster.pcode

    The LLM will see these and use them when generating SQL.
    """

    graph = _load_join_graph()

    q = question.lower()

    # Candidate tables: those whose table-name appears in the question text
    candidate_tables = []
    for full_table in graph.keys():
        schema, name = full_table.split(".", 1)
        if name.lower() in q:
            candidate_tables.append(full_table)

    # If no table name explicitly in the question, just return top edges (generic hints)
    if not candidate_tables:
        # Take a few high-score edges as generic patterns
        pairs = []
        for table, edges in graph.items():
            for e in edges:
                pairs.append(e)
        # sort by score descending, unique them
        seen = set()
        lines = []
        for e in sorted(pairs, key=lambda x: x["score"], reverse=True):
            key = (e["left"], e["right"], e["left_column"], e["right_column"])
            if key in seen:
                continue
            seen.add(key)
            lines.append(
                f"- Join {e['left']} and {e['right']} ON "
                f"{e['left']}.{e['left_column']} = {e['right']}.{e['right_column']} "
                f"({e['source']})"
            )
            if len(lines) >= max_pairs:
                break
        return "\n".join(lines)

    # If we have candidate tables, create hints only for them
    lines: List[str] = []
    seen_pairs = set()

    for i in range(len(candidate_tables)):
        t1 = candidate_tables[i]
        for e in graph.get(t1, []):
            t2 = e["right"]
            if t2 not in candidate_tables:
                continue

            key = tuple(sorted([t1, t2]) + [e["left_column"], e["right_column"]])
            if key in seen_pairs:
                continue

            seen_pairs.add(key)
            lines.append(
                f"- Join {t1} and {t2} ON "
                f"{t1}.{e['left_column']} = {t2}.{e['right_column']} "
                f"({e['source']})"
            )
            if len(lines) >= max_pairs:
                break

    return "\n".join(lines)
