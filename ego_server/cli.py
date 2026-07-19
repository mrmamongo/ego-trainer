"""ego-server CLI — separate entry-point from the ``ego`` client.

Per ADR-0001 D13 there are three independent entry-points:
- ``ego``        — client (student): init/list/check/pull/push.
- ``ego-server`` — server: run (uvicorn), migrate, admin (create-user/import-tasks/list-users).
- ``ego-tui``    — TUI (textual), post-MVP.

This module implements the ``ego-server`` CLI. It deliberately keeps all
heavy imports (uvicorn, db, auth, parser) *lazy* (inside command functions)
so that ``--help`` / ``--version`` work without the server extras installed,
and so the module is cheap to import from tests.

Design notes for parallel work (see task ego-trainer-bmh.8):
- ``ego_server.auth`` is implemented by task bmh.2 (Server.2). It may not
  exist yet when this code runs. ``_load_auth`` falls back to a local
  implementation (uuid4 + sha256) so ``create-user`` works during the
  parallel window; once ``ego_server.auth`` lands the real (bcrypt)
  implementation is used automatically.
- ``settings`` is accessed dynamically via ``ego_server.config`` (never
  bound at module top level) so ``importlib.reload`` in test fixtures
  propagates the temp DB path to already-imported CLI code.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from ego_server import __version__


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="ego-server",
        description="Ego server — catalog/progress/auth. See ADR-0001 D13.",
    )
    parser.add_argument(
        "--version", action="version", version=f"ego-server {__version__}"
    )
    sub = parser.add_subparsers(dest="command")

    # run
    p_run = sub.add_parser("run", help="Start the FastAPI server (uvicorn)")
    p_run.add_argument("--host", default="0.0.0.0")
    p_run.add_argument("--port", type=int, default=8000)
    p_run.add_argument(
        "--reload", action="store_true", help="Auto-reload on file changes (dev)"
    )

    # migrate
    sub.add_parser("migrate", help="Initialize/update database schema")

    # admin
    p_admin = sub.add_parser("admin", help="Administrative commands")
    admin_sub = p_admin.add_subparsers(dest="admin_command")

    p_create = admin_sub.add_parser("create-user", help="Create a new user")
    p_create.add_argument("--username", required=True)
    p_create.add_argument("--password", required=True)
    p_create.add_argument(
        "--role", default="student", choices=["student", "mentor", "admin"]
    )

    p_import = admin_sub.add_parser("import-tasks", help="Import .md tasks into DB")
    p_import.add_argument(
        "--docs-dir", default="docs/tasks", help="Path to tasks directory"
    )
    p_import.add_argument(
        "--force",
        action="store_true",
        help="Re-import even if content_hash matches",
    )

    admin_sub.add_parser("list-users", help="List all users")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "run":
        return _cmd_run(args)
    if args.command == "migrate":
        return _cmd_migrate(args)
    if args.command == "admin":
        if args.admin_command is None:
            p_admin.print_help()
            return 1
        if args.admin_command == "create-user":
            return _cmd_create_user(args)
        if args.admin_command == "import-tasks":
            return _cmd_import_tasks(args)
        if args.admin_command == "list-users":
            return _cmd_list_users(args)

    parser.print_help()
    return 0


def _cmd_run(args) -> int:
    """Start uvicorn (dev server)."""
    import uvicorn

    uvicorn.run(
        "ego_server.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


def _cmd_migrate(args) -> int:
    """Apply schema.sql to the configured database."""
    from ego_server import config
    from ego_server.db import init_db

    init_db()
    print(f"Schema applied to {config.settings.db_path}")
    return 0


def _cmd_create_user(args) -> int:
    """Create a user in the DB (with hashed password)."""
    from ego_server.db import get_connection

    generate_user_id, hash_password = _load_auth()

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM students WHERE username = ?", (args.username,)
        ).fetchone()
        if existing:
            print(f"User '{args.username}' already exists", file=sys.stderr)
            return 1
        user_id = generate_user_id()
        pwd_hash = hash_password(args.password)
        now = _now_iso()
        conn.execute(
            "INSERT INTO students (id, username, role, password_hash, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, args.username, args.role, pwd_hash, now),
        )
        conn.commit()
        print(f"Created user '{args.username}' (id={user_id}, role={args.role})")
        return 0
    finally:
        conn.close()


def _cmd_import_tasks(args) -> int:
    """Import ``.md`` tasks from a docs directory into the DB.

    Uses ``ego.parser`` to read each ``.md``, computes ``content_hash``,
    and inserts/updates rows in the ``tasks`` table via
    :func:`ego_server.db_helpers.upsert_task`. When the content changed
    (or ``--force`` is set) the minor version is bumped (ADR-0001 D3).
    """
    from ego.parser import parse_task_file
    from ego_server.db import get_connection
    from ego_server.db_helpers import upsert_task

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        print(f"docs dir not found: {docs_dir.resolve()}", file=sys.stderr)
        return 1

    md_files = sorted(docs_dir.rglob("*.md"))
    if not md_files:
        print(f"no .md files under {docs_dir.resolve()}", file=sys.stderr)
        return 1

    conn = get_connection()
    try:
        imported = 0
        updated = 0
        skipped = 0
        for md_path in md_files:
            try:
                task = parse_task_file(md_path)
            except Exception as e:  # noqa: BLE001 — skip unparseable files
                print(f"  SKIP {md_path.name}: parse error: {e}", file=sys.stderr)
                continue

            result = upsert_task(conn, task, force=args.force)
            if result == "imported":
                imported += 1
                print(f"  + {task.id}: {task.title} (new, v{task.version})")
            elif result == "updated":
                updated += 1
                print(f"  ~ {task.id}: {task.title} (updated)")
            elif result == "skipped":
                skipped += 1
                print(f"  = {task.id}: {task.title} (unchanged)")

        conn.commit()
        print(f"\nImported: {imported}, Updated: {updated}, Skipped: {skipped}")
        return 0
    finally:
        conn.close()


def _cmd_list_users(args) -> int:
    """List all users ordered by username."""
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT username, role, created_at, last_login_at "
            "FROM students ORDER BY username"
        ).fetchall()
        if not rows:
            print("(no users)")
            return 0
        print(f"{'USERNAME':<20} {'ROLE':<10} {'CREATED':<26} {'LAST LOGIN'}")
        print("-" * 80)
        for r in rows:
            print(
                f"{r['username']:<20} {r['role']:<10} {r['created_at']:<26} "
                f"{r['last_login_at'] or '—'}"
            )
        print(f"\n{len(rows)} users")
        return 0
    finally:
        conn.close()


# === Internal helpers ===


def _load_auth():
    """Return ``(generate_user_id, hash_password)``.

    Prefer ``ego_server.auth`` (task bmh.2 / Server.2). If that module is not
    available yet (parallel work in progress), fall back to a local
    uuid4 + sha256 implementation so ``create-user`` keeps working. The
    fallback is only used until ``ego_server.auth`` is importable.
    """
    try:
        from ego_server.auth import generate_user_id, hash_password

        return generate_user_id, hash_password
    except ImportError:
        import hashlib
        import uuid

        def generate_user_id() -> str:
            return str(uuid.uuid4())

        def hash_password(password: str) -> str:
            return hashlib.sha256(password.encode("utf-8")).hexdigest()

        return generate_user_id, hash_password


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    sys.exit(main())
