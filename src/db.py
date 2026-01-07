import sqlite3
from pathlib import Path

def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def exec_schema(conn: sqlite3.Connection, schema_path: str = "schema.sql") -> None:
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
