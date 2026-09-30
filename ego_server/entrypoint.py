"""Production container entrypoint: validate, migrate, sync, then exec Uvicorn."""

from __future__ import annotations

import os
import sqlite3


def prepare_startup() -> None:
    """Validate production settings and prepare persistent state."""
    from ego_server.config import settings, validate_runtime_settings
    from ego_server.service_settings import effective_content_config
    from ego_server.db import get_connection, init_db
    from ego_server.sync import sync_from_config

    validate_runtime_settings(settings)
    init_db()

    conn: sqlite3.Connection = get_connection()
    try:
        content_config = effective_content_config(conn)
        if not content_config.url:
            raise RuntimeError("Configure a local content directory before starting the service")
        result = sync_from_config(conn, content_config, source="startup")
        if result.errors or result.status == "failed":
            conn.rollback()
            raise RuntimeError(
                f"task content sync failed: status={result.status}, "
                f"errors={result.errors}: {result.error_details_text}"
            )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    """Prepare state and replace this process with a production Uvicorn worker."""
    from ego_server.config import settings

    prepare_startup()
    argv = [
        "uvicorn",
        "ego_server.main:app",
        "--host",
        settings.bind_host,
        "--port",
        str(settings.bind_port),
        "--workers",
        str(settings.uvicorn_workers),
        "--no-server-header",
    ]
    os.execvp(argv[0], argv)


if __name__ == "__main__":
    main()
