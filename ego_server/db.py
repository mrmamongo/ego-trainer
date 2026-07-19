"""SQLite connection and schema initialization."""

import sqlite3
from pathlib import Path

from ego_server.config import settings


SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection. Creates parent dir if needed."""
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Apply schema.sql to the database (idempotent)."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def init_db() -> None:
    """Initialize the database (call on app startup)."""
    conn = get_connection()
    try:
        init_schema(conn)
    finally:
        conn.close()
