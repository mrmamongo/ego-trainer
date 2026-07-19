"""Check router — POST /check: run checker server-side.

Per ADR-0014: VSCode extension sends student code to server, server runs
the checker in sandbox and returns CheckResponse. Server also stores
progress + run log (same as POST /progress/push, but server-side check).

Security: student code runs in sandbox (timeout 5s, no network, blocked
imports, temp dir). For prod — Docker container per check (ADR-0014).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from ego.checker import format_check_result, run_check
from ego.parser import parse_task_file
from ego_server.db_helpers import get_task_meta
from ego_server.deps import CurrentUser, DbDep
from ego_server.models import CheckRequest, CheckResponse, TestResultDTO


router = APIRouter()


@router.post("", response_model=CheckResponse)
async def check_solution(
    body: CheckRequest, db: DbDep, user: CurrentUser
) -> CheckResponse:
    """Run checker server-side. Student sends code, server runs it.

    Flow:
        1. Validate task exists in DB
        2. Parse .md -> Task (parser)
        3. run_check(task, student_code) -> CheckResult
        4. Store progress + run log
        5. Return CheckResponse
    """
    student_id = user["sub"]

    # 1. Validate task exists.
    meta = get_task_meta(db, body.task_id)
    if meta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{body.task_id}' not found",
        )

    # 2. Parse .md -> Task.
    from ego_server.routers.tasks import _resolve_md_path

    md_path = _resolve_md_path(meta["md_path"])
    if not md_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task .md file not found at {meta['md_path']}",
        )

    task = parse_task_file(md_path)

    # 3. Run checker (sandbox: timeout 5s, no network, temp dir).
    result = run_check(task, body.student_code, timeout=5.0)

    # 4. Store progress + run log.
    now = datetime.now(timezone.utc).isoformat()
    _store_progress(
        db, student_id, body.task_id, meta["version"], result, now
    )

    # 5. Build response.
    log = format_check_result(result)
    return CheckResponse(
        task_id=result.task_id,
        version=result.version,
        status=result.status,
        passed_tests=result.passed_tests,
        total_tests=result.total_tests,
        solution_hash=result.solution_hash,
        results=[
            TestResultDTO(
                description=tr.description,
                passed=tr.passed,
                expected_repr=tr.expected_repr,
                actual_repr=tr.actual_repr,
                error=tr.error,
            )
            for tr in result.results
        ],
        log=log,
    )


def _store_progress(db, student_id: str, task_id: str, version: str, result, now: str) -> None:
    """Upsert progress + insert run log (same logic as POST /progress/push)."""
    # Map checker status to progress status.
    status_map = {
        "passed": "passed",
        "partial": "partial",
        "failed": "failed",
        "error": "error",
        "timeout": "timeout",
        "no_tests": "error",
    }
    prog_status = status_map.get(result.status, "error")

    existing = db.execute(
        "SELECT attempts FROM progress WHERE student_id = ? AND task_id = ? AND version = ?",
        (student_id, task_id, version),
    ).fetchone()

    if existing is None:
        attempts = 1
        db.execute(
            """INSERT INTO progress
            (student_id, task_id, version, status, attempts,
             passed_tests, total_tests, last_run_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (student_id, task_id, version, prog_status, attempts,
             result.passed_tests, result.total_tests, now),
        )
    else:
        attempts = existing["attempts"] + 1
        db.execute(
            """UPDATE progress SET
            status = ?, attempts = ?, passed_tests = ?,
            total_tests = ?, last_run_at = ?
            WHERE student_id = ? AND task_id = ? AND version = ?""",
            (prog_status, attempts, result.passed_tests, result.total_tests,
             now, student_id, task_id, version),
        )

    # Insert run log.
    run_id = uuid.uuid4().hex[:12]
    log_text = format_check_result(result)
    db.execute(
        """INSERT INTO runs
        (id, student_id, task_id, version, solution_hash, status, log, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id, student_id, task_id, version, result.solution_hash,
         prog_status, log_text[:8192], now),
    )
    db.commit()
