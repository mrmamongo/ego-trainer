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
    conn.executescript(SCHEMA_PATH.with_name("ai_schema.sql").read_text(encoding="utf-8"))
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
    if "archived" not in tasks_cols:
        conn.execute("ALTER TABLE tasks ADD COLUMN archived INTEGER NOT NULL DEFAULT 0")
    # tasks.theory: JSON array of lesson ids (theory cards before the task)
    if "theory" not in tasks_cols:
        conn.execute("ALTER TABLE tasks ADD COLUMN theory TEXT NOT NULL DEFAULT '[]'")

    projects_cols = {row["name"] for row in conn.execute("PRAGMA table_info(projects)")}
    if "archived" not in projects_cols:
        conn.execute("ALTER TABLE projects ADD COLUMN archived INTEGER NOT NULL DEFAULT 0")

    oauth_cols = {row["name"] for row in conn.execute("PRAGMA table_info(oauth_flows)")}
    if "callback_uri" not in oauth_cols:
        conn.execute("ALTER TABLE oauth_flows ADD COLUMN callback_uri TEXT")

    _migrate_add_lessons_table(conn)
    _migrate_add_analytics_table(conn)


def _migrate_add_lessons_table(conn: sqlite3.Connection) -> None:
    """Create ``lessons`` (+ indexes) on databases predating theory cards.

    ``CREATE TABLE IF NOT EXISTS`` in ``schema.sql`` already covers this for
    any older DB; the explicit statement keeps the guarantee local to the
    migration path (e.g. a DB initialized from an older ``schema.sql``
    copy without re-running the full script).
    """
    conn.execute(
        """CREATE TABLE IF NOT EXISTS lessons (
          id           TEXT PRIMARY KEY,
          project_id   TEXT NOT NULL,
          folder_id    TEXT NOT NULL,
          title        TEXT NOT NULL DEFAULT '',
          "order"      INTEGER NOT NULL DEFAULT 0,
          version      TEXT NOT NULL DEFAULT '1.0.0',
          content_hash TEXT NOT NULL,
          body_md      TEXT NOT NULL DEFAULT '',
          created_at   TEXT NOT NULL,
          updated_at   TEXT NOT NULL
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lessons_project ON lessons(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lessons_folder ON lessons(folder_id)")


def _migrate_add_analytics_table(conn: sqlite3.Connection) -> None:
    """Add daily, privacy-preserving counters without changing existing tables."""
    conn.execute(
        """CREATE TABLE IF NOT EXISTS analytics_daily (
          day       TEXT NOT NULL,
          metric    TEXT NOT NULL,
          key       TEXT NOT NULL DEFAULT '',
          count     INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY(day, metric, key)
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_analytics_metric_day ON analytics_daily(metric, day)"
    )


def init_db() -> None:
    """Initialize the database (call on app startup)."""
    conn = get_connection()
    try:
        init_schema(conn)
    finally:
        conn.close()
