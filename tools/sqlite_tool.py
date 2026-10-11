import os
import sqlite3
import csv
from typing import Any


def open_database(path: str, read_only: bool = True) -> sqlite3.Connection:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    if read_only:
        uri = f"file:{path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=5.0)
    else:
        conn = sqlite3.connect(path, timeout=5.0)

    conn.row_factory = sqlite3.Row
    return conn


def is_sqlite_file(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        return head.startswith(b"SQLite format 3\x00")
    except OSError:
        return False

def list_tables(conn: sqlite3.Connection) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, type FROM sqlite_master
        WHERE type IN ('table', 'view')
          AND name NOT LIKE 'sqlite_%'
        ORDER BY type, name
    """)
    items = cursor.fetchall()

    result = []
    for row in items:
        name = row["name"]
        typ = row["type"]
        count = None
        if typ == "table":
            try:
                c2 = conn.cursor()
                c2.execute(f'SELECT COUNT(*) AS n FROM "{name}"')
                count = c2.fetchone()["n"]
            except sqlite3.Error:
                count = None
        result.append({"name": name, "type": typ, "rows": count})
    return result


def table_schema(conn: sqlite3.Connection, table: str) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA table_info("{table}")')
    return [
        {
            "name": row["name"],
            "type": row["type"] or "",
            "notnull": bool(row["notnull"]),
            "pk": bool(row["pk"]),
            "default": row["dflt_value"],
        }
        for row in cursor.fetchall()
    ]


def read_rows(
    conn: sqlite3.Connection,
    table: str,
    offset: int = 0,
    limit: int = 100,
    order_by: str | None = None,
    descending: bool = False,
) -> list[dict]:
    order_clause = ""
    if order_by:
        direction = "DESC" if descending else "ASC"
        order_clause = f' ORDER BY "{order_by}" {direction}'

    cursor = conn.cursor()
    cursor.execute(
        f'SELECT * FROM "{table}"{order_clause} LIMIT ? OFFSET ?',
        (limit, offset),
    )
    return [dict(row) for row in cursor.fetchall()]


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    cursor = conn.cursor()
    cursor.execute(f'SELECT COUNT(*) AS n FROM "{table}"')
    return cursor.fetchone()["n"]


def execute_query(conn: sqlite3.Connection, sql: str,
                  params: tuple = ()) -> dict:
    cursor = conn.cursor()
    sql_stripped = sql.strip().lower()

    is_select = sql_stripped.startswith(("select", "pragma", "with", "explain"))
    is_returning = "returning" in sql_stripped

    try:
        if is_select or is_returning:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            columns = (
                [d[0] for d in cursor.description]
                if cursor.description else []
            )
            return {
                "ok": True, "error": None,
                "columns": columns,
                "rows": [list(r) for r in rows],
                "rowcount": len(rows),
                "is_select": True,
            }
        else:
            cursor.execute(sql, params)
            conn.commit()
            return {
                "ok": True, "error": None,
                "columns": [],
                "rows": [],
                "rowcount": cursor.rowcount,
                "is_select": False,
            }
    except sqlite3.Error as e:
        return {
            "ok": False, "error": str(e),
            "columns": [], "rows": [],
            "rowcount": 0, "is_select": is_select,
        }


def update_cell(
    conn: sqlite3.Connection,
    table: str,
    pk_column: str,
    pk_value: Any,
    column: str,
    new_value: Any,
) -> tuple[bool, str | None]:
    try:
        cursor = conn.cursor()
        cursor.execute(
            f'UPDATE "{table}" SET "{column}" = ? WHERE "{pk_column}" = ?',
            (new_value, pk_value),
        )
        conn.commit()
        return True, None
    except sqlite3.Error as e:
        return False, str(e)


def delete_row(
    conn: sqlite3.Connection,
    table: str,
    pk_column: str,
    pk_value: Any,
) -> tuple[bool, str | None]:
    try:
        cursor = conn.cursor()
        cursor.execute(
            f'DELETE FROM "{table}" WHERE "{pk_column}" = ?',
            (pk_value,),
        )
        conn.commit()
        return True, None
    except sqlite3.Error as e:
        return False, str(e)


def export_csv(
    columns: list[str],
    rows: list[list],
    path: str,
) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for r in rows:
            writer.writerow(r)


def format_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bytes):
        if len(value) <= 32:
            return value.hex()
        return f"<BLOB {len(value)} байт>"
    return str(value)