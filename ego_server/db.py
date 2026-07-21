"""SQLite connection and schema initialization."""

import sqlite3
from pathlib import Path

from ego_server.config import settings


SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection. Creates parent dir if needed.

    check_same_thread=False because FastAPI may handle requests in
    different threads (especially TestClient). Callers must not share
    a connection across requests — use get_db() dependency which closes
    after each request.
    """
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Apply schema.sql to the database (idempotent).

    Also runs ``_migrate_add_columns`` for forward-compatible schema
    evolution (``CREATE TABLE IF NOT EXISTS`` does not add new columns
    to existing tables).
    """
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    _migrate_add_columns(conn)
    conn.commit()


def _migrate_add_columns(conn: sqlite3.Connection) -> None:
    """Add columns introduced after the initial schema (idempotent).

    ``CREATE TABLE IF NOT EXISTS`` won't add new columns to an existing
    table, so we use ``ALTER TABLE ... ADD COLUMN`` guarded by a check
    on ``PRAGMA table_info``.
    """
    # tasks.folder_id, tasks.project_id (ADR-0016 D16.6)
    tasks_cols = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
    if "folder_id" not in tasks_cols:
        conn.execute("ALTER TABLE tasks ADD COLUMN folder_id TEXT")
    if "project_id" not in tasks_cols:
        conn.execute("ALTER TABLE tasks ADD COLUMN project_id TEXT")


def init_db() -> None:
    """Initialize the database (call on app startup)."""
    conn = get_connection()
    try:
        init_schema(conn)
    finally:
        conn.close()
