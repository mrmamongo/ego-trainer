"""Admin router — content-repo sync (ADR-0016 D16.2, D16.4).

PR 1: local sync only (``POST /admin/sync-tasks`` with a local path).
PR 2 will add git URL support + cron-triggered sync.

All endpoints require ``admin`` role (per ADR-0001 D8).
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from ego_server.deps import DbDep, require_role
from ego_server.models import SyncLogRow, SyncResultDTO, SyncTasksRequest
from ego_server.sync import sync_from_path

router = APIRouter()


@router.post(
    "/sync-tasks",
    response_model=SyncResultDTO,
    dependencies=[Depends(require_role("admin"))],
)
async def sync_tasks(req: SyncTasksRequest, db: DbDep) -> SyncResultDTO:
    """Sync content-repo at ``req.path`` into DB (PR 1: local path only).

    Triggers a full walk + upsert cycle. Returns counts (added/updated/
    skipped/errors) and a ``sync_log`` row id.

    Per ADR-0016 D16.5: ``path`` may be a local filesystem path or a
    ``file://`` URL. Git remote sync (``https://``) is implemented in PR 2.
    """
    repo_path = _resolve_path(req.path)
    if not repo_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"path not found or not a directory: {repo_path}",
        )

    result = sync_from_path(
        db, repo_path, source=req.source, repo_url=str(repo_path)
    )
    db.commit()

    return _to_dto(result, repo_url=str(repo_path))


@router.get(
    "/sync/log",
    response_model=list[SyncLogRow],
    dependencies=[Depends(require_role("admin", "mentor"))],
)
async def get_sync_log(db: DbDep, limit: int = 50) -> list[SyncLogRow]:
    """Return recent sync_log rows (newest first, default 50)."""
    if limit < 1 or limit > 500:
        limit = 50
    rows = db.execute(
        """SELECT id, started_at, finished_at, source, repo_url, git_sha,
                  status, added, updated, skipped, errors, error_details
           FROM sync_log ORDER BY id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    return [SyncLogRow(**dict(r)) for r in rows]


@router.get(
    "/sync/status",
    response_model=SyncLogRow | None,
    dependencies=[Depends(require_role("admin", "mentor"))],
)
async def get_sync_status(db: DbDep) -> SyncLogRow | None:
    """Return the most recent sync_log row (or null if no syncs yet)."""
    row = db.execute(
        """SELECT id, started_at, finished_at, source, repo_url, git_sha,
                  status, added, updated, skipped, errors, error_details
           FROM sync_log ORDER BY id DESC LIMIT 1"""
    ).fetchone()
    if row is None:
        return None
    return SyncLogRow(**dict(row))


# === Helpers ===


def _resolve_path(path_str: str) -> Path:
    """Resolve a path that may be a ``file://`` URL or a bare local path.

    Handles Windows-style paths where a drive letter (``C:``) may appear
    in the URL. Accepts both ``file:///C:/path`` (triple slash, RFC) and
    ``file://C:/path`` (common but non-RFC) forms.
    """
    if path_str.startswith("file://"):
        from urllib.parse import urlparse
        import sys

        parsed = urlparse(path_str)
        # Reconstruct path: on Windows, urlparse may put 'C:' in netloc
        # for 'file://C:/path' (non-RFC form). Prefer netloc+path if so.
        if parsed.netloc and sys.platform == "win32" and len(parsed.netloc) >= 2 and parsed.netloc[1] == ":":
            p = parsed.netloc + parsed.path
        else:
            p = parsed.path
            # file:///C:/path → parsed.path = '/C:/path' → strip leading slash.
            if sys.platform == "win32" and len(p) >= 3 and p[0] == "/" and p[2] == ":":
                p = p[1:]
        return Path(p)
    return Path(path_str)


def _to_dto(result, *, repo_url: str) -> SyncResultDTO:
    """Convert :class:`ego_server.sync.SyncResult` to :class:`SyncResultDTO`."""
    return SyncResultDTO(
        log_id=result.log_id or 0,
        status=result.status,
        added=result.added,
        updated=result.updated,
        skipped=result.skipped,
        errors=result.errors,
        error_details=result.error_details_text,
        started_at=result.started_at,
        finished_at=result.finished_at,
        git_sha=result.git_sha,
        repo_url=repo_url,
    )
