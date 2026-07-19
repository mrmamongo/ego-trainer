"""Progress router — POST /progress/push (bmh.4) and GET /progress/<student> (bmh.5).

POST /progress/push:
  - Student sends their check result (task_id, version, status, tests, log).
  - Server validates: task exists, student exists, hash present.
  - Upserts into progress table (student_id, task_id, version).
  - Inserts into runs table (full log).
  - Returns the stored ProgressRow.

GET /progress/<student_id>:
  - Mentor/admin only: list all progress entries for a student.
  - Implemented in bmh.5 (currently 501).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ego_server.deps import CurrentUser, DbDep, require_role
from ego_server.models import ProgressPush, ProgressRow


router = APIRouter()


@router.post("/push", response_model=ProgressRow)
async def push_progress(body: ProgressPush, db: DbDep, user: CurrentUser) -> ProgressRow:
    """Receive a check result from a student, store progress + run log.

    The student's JWT identifies them (user["sub"] = student_id).
    Validates that the task exists in the DB before storing.
    """
    student_id = user["sub"]

    # Validate task exists.
    task_row = db.execute(
        "SELECT id FROM tasks WHERE id = ?", (body.task_id,)
    ).fetchone()
    if task_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{body.task_id}' not found",
        )

    # Validate solution_hash is non-empty.
    if not body.solution_hash:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="solution_hash is required",
        )

    now = datetime.now(timezone.utc).isoformat()

    # Upsert progress (student_id, task_id, version).
    existing = db.execute(
        "SELECT attempts FROM progress WHERE student_id = ? AND task_id = ? AND version = ?",
        (student_id, body.task_id, body.version),
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
                body.task_id,
                body.version,
                body.status,
                attempts,
                body.passed_tests,
                body.total_tests,
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
                body.status,
                attempts,
                body.passed_tests,
                body.total_tests,
                now,
                student_id,
                body.task_id,
                body.version,
            ),
        )

    # Insert run log.
    import uuid

    run_id = uuid.uuid4().hex[:12]
    db.execute(
        """INSERT INTO runs
        (id, student_id, task_id, version, solution_hash, status, log, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            run_id,
            student_id,
            body.task_id,
            body.version,
            body.solution_hash,
            body.status,
            body.log[:8192],  # truncate to 8KB
            now,
        ),
    )

    db.commit()

    return ProgressRow(
        student_id=student_id,
        task_id=body.task_id,
        version=body.version,
        status=body.status,
        attempts=attempts,
        passed_tests=body.passed_tests,
        total_tests=body.total_tests,
        last_run_at=now,
    )


@router.get("/{student_id}", response_model=list[ProgressRow])
async def get_progress(
    student_id: str,
    db: DbDep,
    user: Annotated[dict, Depends(require_role("mentor", "admin"))],
) -> list[ProgressRow]:
    """List all progress entries for a student. Mentors/admins only.

    Implemented in bmh.5.
    """
    rows = db.execute(
        """SELECT student_id, task_id, version, status, attempts,
                  passed_tests, total_tests, last_run_at
           FROM progress WHERE student_id = ?
           ORDER BY task_id, version""",
        (student_id,),
    ).fetchall()
    return [
        ProgressRow(
            student_id=r["student_id"],
            task_id=r["task_id"],
            version=r["version"],
            status=r["status"],
            attempts=r["attempts"],
            passed_tests=r["passed_tests"],
            total_tests=r["total_tests"],
            last_run_at=r["last_run_at"],
        )
        for r in rows
    ]
