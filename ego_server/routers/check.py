"""Check router — POST /check: run checker server-side.

Per ADR-0014: VSCode extension sends student code to server, server runs
the checker in sandbox and returns CheckResponse. Server also stores
progress + run log (same as POST /progress/push, but server-side check).

Two shapes of a submission (ADR-0018 D18.5):

- ``student_code`` — one function of an ordinary single-file task
  (:func:`ego.checker.run_check`, unchanged);
- ``files`` — ``{path: source}`` of a challenge stage
  (:func:`ego.checker.run_stage_check`): the tests of stages 1..N run
  against the project, every result names its stage, and progress is
  written for stage N only.

Security: student code runs in sandbox (timeout 5s, no network, blocked
imports, temp dir). For prod — Docker container per check (ADR-0014).
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from ego.checker import (
    StageTests,
    format_check_result,
    format_stage_check_result,
    run_check,
    run_stage_check,
)
from ego.parser import parse_task_file
from ego.runner import project_view
from ego_server.catalog_visibility import ACTIVE_TASK_FILTER
from ego_server.db_helpers import get_task_meta
from ego_server.deps import CurrentUser, DbDep
from ego_server.models import CheckRequest, CheckResponse, TestResultDTO
from ego_server.service_settings import load_settings


router = APIRouter()

#: Shown to an old extension that sends ``student_code`` for a stage.
STAGE_NEEDS_FILES = (
    "этот этап проверяется только новой версией Cogito — обнови расширение"
)


@router.post("", response_model=CheckResponse)
async def check_solution(body: CheckRequest, db: DbDep, user: CurrentUser) -> CheckResponse:
    """Run checker server-side. Student sends code (or a project), server runs it.

    Flow:
        1. Validate the task exists in DB
        2. Parse .md -> Task (parser)
        3. run_check / run_stage_check -> CheckResult
        4. Store progress + run log
        5. Return CheckResponse
    """
    student_id = user["sub"]
    config = load_settings(db)

    # 1. Validate task exists.
    meta = get_task_meta(db, body.task_id)
    if meta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{body.task_id}' not found",
        )
    stage_number = meta.get("challenge_stage")
    stage = _submission_shape(body, stage_number)

    # 2. Parse .md -> Task.
    from ego_server.routers.tasks import _resolve_md_path

    md_path = _resolve_md_path(meta["md_path"])
    if not md_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task .md file not found at {meta['md_path']}",
        )

    task = parse_task_file(md_path)
    files = body.files if stage == "files" else None
    code = _code_text(stage, body, files)
    if len(code) > config.max_code_chars:
        raise HTTPException(
            status_code=413, detail="Student code exceeds the configured size limit"
        )

    # 3. Run checker (sandbox: timeout 5s, no network, temp dir).
    if stage == "files":
        stages, workspace = _challenge(db, meta)
        try:
            result = await run_in_threadpool(
                run_stage_check,
                task,
                files,
                stages=stages,
                timeout=config.check_timeout_seconds,
                workspace=workspace,
            )
        except ValueError as exc:  # SandboxError: unsafe paths / limits
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        log = format_stage_check_result(result)
    else:
        assert body.student_code is not None  # _submission_shape guarantees it
        workspace = None
        result = await run_in_threadpool(
            run_check, task, body.student_code, timeout=config.check_timeout_seconds
        )
        log = format_check_result(result)

    # 4. Store progress + run log.
    now = datetime.now(timezone.utc).isoformat()
    _store_progress(
        db,
        student_id,
        body.task_id,
        meta["version"],
        result,
        now,
        log=log,
        files=files,
    )

    from ego_server.ai import record_submission

    understanding = record_submission(
        db, student_id, body.task_id, meta["version"], result, code, task
    )

    # 5. Build response.
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
                stage=tr.stage,
                stage_title=tr.stage_title,
            )
            for tr in result.results
        ],
        log=log,
        understanding=understanding,
    )


# === Submission shape (ADR-0018 D18.5) ===


def _submission_shape(body: CheckRequest, stage_number: int | None) -> str:
    """``"files"`` or ``"code"``; 422 with a Russian message for anything else.

    A challenge stage takes only ``files`` (an old extension gets
    :data:`STAGE_NEEDS_FILES`), an ordinary task takes only ``student_code``.
    """
    has_code = body.student_code is not None
    has_files = body.files is not None
    if has_code and has_files:
        raise HTTPException(
            status_code=422,
            detail="Передай что-то одно: student_code (одна функция) "
            "или files (проект этапа), а не оба сразу",
        )
    if not has_code and not has_files:
        raise HTTPException(
            status_code=422,
            detail="Нужен student_code (одна функция) или files (проект этапа)",
        )
    if stage_number is not None:
        if has_code:
            raise HTTPException(status_code=422, detail=STAGE_NEEDS_FILES)
        return "files"
    if has_files:
        raise HTTPException(
            status_code=422,
            detail="files принимаются только для этапа челленджа; "
            "для обычной задачи передай student_code",
        )
    return "code"


def _code_text(shape: str, body: CheckRequest, files: dict[str, str] | None) -> str:
    """The submission's source text: the file or the concatenated project."""
    if shape == "files":
        return project_view(files or {})
    return body.student_code or ""


def _challenge(db, meta: dict) -> tuple[list[StageTests], dict | None]:
    """Stages of the task's challenge (in order) + its workspace spec."""
    folder = db.execute(
        'SELECT kind, workspace_json FROM folders WHERE id = ? AND project_id = ?',
        (meta["folder_id"], meta["project_id"]),
    ).fetchone()
    if folder is None or folder["kind"] != "challenge":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Challenge folder of '{meta['id']}' is missing in the DB; re-sync the content",
        )
    rows = db.execute(
        f"""SELECT id, title, challenge_stage, md_path FROM tasks
            WHERE folder_id = ? AND project_id = ?
              AND challenge_stage IS NOT NULL AND {ACTIVE_TASK_FILTER}
            ORDER BY challenge_stage""",
        (meta["folder_id"], meta["project_id"]),
    ).fetchall()
    from ego_server.routers.tasks import _resolve_md_path

    stages = [
        StageTests(
            task=parse_task_file(_resolve_md_path(row["md_path"])),
            number=int(row["challenge_stage"]),
            title=row["title"],
        )
        for row in rows
    ]
    workspace = json.loads(folder["workspace_json"]) if folder["workspace_json"] else None
    return stages, workspace


# === Progress + run log ===


def _store_progress(
    db: sqlite3.Connection,
    student_id: str,
    task_id: str,
    version: str,
    result,
    now: str,
    *,
    log: str | None = None,
    files: dict[str, str] | None = None,
) -> None:
    """Upsert progress + insert run log (same logic as POST /progress/push).

    ``files`` (a challenge submission) is kept whole in ``runs.files_json``;
    ``log`` defaults to :func:`format_check_result` of the result.
    """
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
    log_text = format_check_result(result) if log is None else log

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
            (
                student_id,
                task_id,
                version,
                prog_status,
                attempts,
                result.passed_tests,
                result.total_tests,
                now,
            ),
        )
    else:
        attempts = existing["attempts"] + 1
        db.execute(
            """UPDATE progress SET
            status = ?, attempts = ?, passed_tests = ?,
            total_tests = ?, last_run_at = ?
            WHERE student_id = ? AND task_id = ? AND version = ?""",
            (
                prog_status,
                attempts,
                result.passed_tests,
                result.total_tests,
                now,
                student_id,
                task_id,
                version,
            ),
        )

    # Insert run log.
    run_id = uuid.uuid4().hex[:12]
    db.execute(
        """INSERT INTO runs
        (id, student_id, task_id, version, solution_hash, status, log,
         files_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            run_id,
            student_id,
            task_id,
            version,
            result.solution_hash,
            prog_status,
            log_text[:8192],
            json.dumps(files, ensure_ascii=False) if files is not None else None,
            now,
        ),
    )
    db.commit()
