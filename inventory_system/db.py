import sqlite3
from pathlib import Path

from flask import g


def get_db_path() -> Path:
    base = Path(__file__).resolve().parent
    return base / "data" / "inventory.db"


def get_connection():
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    schema = Path(__file__).resolve().parent / "schema.sql"
    conn = get_connection()
    try:
        conn.executescript(schema.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


def close_db(e=None):
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()


def db_conn():
    if "db_conn" not in g:
        g.db_conn = get_connection()
    return g.db_conn
