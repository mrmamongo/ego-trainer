"""Helpers for converting ``ego.models.Task`` to DB rows (and back).

These helpers bridge the ego core parser output (``ego.models.Task``) and
the server's SQLite schema (``tasks`` / ``task_versions`` tables). They live
in ``ego_server`` (not ``ego``) because they encode the *server* schema —
see ADR-0001 D2 (git canonical) and D3 (SemVer).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from ego.models import Task


def upsert_task(conn: sqlite3.Connection, task: Task, *, force: bool = False) -> str:
    """Insert or update a task in the ``tasks`` table.

    Args:
        conn: SQLite connection (``row_factory`` should be ``sqlite3.Row``).
        task: ``ego.models.Task`` produced by the parser.
        force: If True, update even if ``content_hash`` matches (re-import).

    Returns:
        ``"imported"``  — new task inserted.
        ``"updated"``   — existing task updated (content changed or ``force=True``).
        ``"skipped"``   — existing task with same ``content_hash``, ``force=False``.

    SemVer logic (per ADR-0001 D3):
        - New task: ``version = task.version`` (default ``"1.0.0"`` from parser).
        - Update with content change: minor bump (``1.0.0`` -> ``1.1.0``).
        - Major bumps for breaking changes are manual (out of scope here).
    """
    now = datetime.now(timezone.utc).isoformat()

    existing = conn.execute(
        "SELECT id, version, content_hash FROM tasks WHERE id = ?",
        (task.id,),
    ).fetchone()

    if existing is None:
        # Insert new task.
        conn.execute(
            """INSERT INTO tasks
            (id, block, slug, task_id, title, level, tags, version,
             content_hash, breaking, md_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.id,
                task.block,
                task.slug,
                task.task_id,
                task.title,
                task.level,
                _dump_tags(task.tags),
                task.version,
                task.content_hash,
                0,
                str(task.md_path),
                now,
                now,
            ),
        )
        # Insert initial version history row.
        conn.execute(
            """INSERT INTO task_versions
            (task_id, version, content_hash, breaking, md_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (task.id, task.version, task.content_hash, 0, str(task.md_path), now),
        )
        return "imported"

    # Existing task — compare hash.
    if existing["content_hash"] == task.content_hash and not force:
        return "skipped"

    # Update — minor version bump.
    old_version = existing["version"]
    new_version = _bump_minor(old_version)

    conn.execute(
        """UPDATE tasks SET
        block = ?, slug = ?, task_id = ?, title = ?, level = ?, tags = ?,
        version = ?, content_hash = ?, md_path = ?, updated_at = ?
        WHERE id = ?""",
        (
            task.block,
            task.slug,
            task.task_id,
            task.title,
            task.level,
            _dump_tags(task.tags),
            new_version,
            task.content_hash,
            str(task.md_path),
            now,
            task.id,
        ),
    )
    conn.execute(
        """INSERT INTO task_versions
        (task_id, version, content_hash, breaking, md_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (task.id, new_version, task.content_hash, 0, str(task.md_path), now),
    )
    return "updated"


def _dump_tags(tags: list[str]) -> str:
    """Serialize tags list as a JSON array string (matches schema ``tags`` column)."""
    return json.dumps(tags, ensure_ascii=False)


def _bump_minor(version: str) -> str:
    """Bump minor version: ``'1.0.0'`` -> ``'1.1.0'``, ``'2.3.1'`` -> ``'2.4.0'``.

    Falls back to ``'1.0.0'`` if the version is not a valid ``MAJOR.MINOR.PATCH``.
    """
    parts = version.split(".")
    if len(parts) != 3:
        return "1.0.0"
    try:
        major, minor, _patch = (int(p) for p in parts)
    except ValueError:
        return "1.0.0"
    return f"{major}.{minor + 1}.0"


def get_task_meta(conn: sqlite3.Connection, task_id: str) -> dict | None:
    """Fetch task metadata by id. Returns a plain dict or ``None``.

    The ``tags`` column is deserialized from JSON text to a list, and
    ``breaking`` is coerced to ``bool``.
    """
    row = conn.execute(
        """SELECT id, block, slug, task_id, title, level, tags, version,
                  content_hash, breaking, md_path, created_at, updated_at
           FROM tasks WHERE id = ?""",
        (task_id,),
    ).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["tags"] = json.loads(d["tags"]) if d["tags"] else []
    d["breaking"] = bool(d["breaking"])
    return d
