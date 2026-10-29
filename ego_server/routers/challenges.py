"""Challenges router — GET /challenges/<folder_id> (ADR-0018 D18.5).

A challenge is a ``kind: challenge`` folder whose ``stage_NN_<slug>.md``
stages are ordinary ``tasks`` rows (``tasks.challenge_stage`` = 1..N), so
the endpoint only reads the catalog: folder meta, ``workspace``, the stages
with the caller's progress and the starting files of ``starter/``.

Auth is the same as ``/tasks``: any logged-in user may read the challenge
of their own content tree. ``starter/`` files are the public skeleton — the
reference lives in ``solution/`` and is never served here.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from ego.catalog import Workspace
from ego.content_repo import read_project_files
from ego.runner import DEFAULT_ENTRY, DEFAULT_INCLUDE
from ego_server.catalog_visibility import ACTIVE_TASK_FILTER
from ego_server.deps import CurrentUser, DbDep
from ego_server.models import (
    ChallengeDTO,
    ChallengeStageDTO,
    ChallengeWorkspaceDTO,
)


router = APIRouter()

#: Progress status of a stage the caller never checked.
NEW_STATUS = "new"


@router.get("/{folder_id}", response_model=ChallengeDTO)
async def get_challenge(folder_id: str, db: DbDep, user: CurrentUser) -> ChallengeDTO:
    """Metadata, workspace, stages (+ progress) and starter files of a challenge.

    Flow:
        1. Find a visible ``kind: challenge`` folder
        2. Read its stages (``challenge_stage``) with the caller's progress
        3. Collect ``starter/`` next to the stage ``.md`` files
    """
    folder = db.execute(
        """SELECT f.id, f.project_id, f.code, f.name, f.description, f."order",
                  f.level, f.kind, f.workspace_json
           FROM folders f
           JOIN projects p ON p.id = f.project_id
           WHERE f.id = ? AND f.kind = 'challenge' AND p.archived = 0
           ORDER BY f.project_id
           LIMIT 1""",
        (folder_id,),
    ).fetchone()
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge '{folder_id}' not found",
        )

    rows = db.execute(
        f"""SELECT tasks.id, tasks.title, tasks.level, tasks.version,
                   tasks.challenge_stage, COALESCE(tasks.theory, '[]') AS theory,
                   tasks.md_path,
                   COALESCE(pr.status, ?) AS status,
                   COALESCE(pr.passed_tests, 0) AS passed_tests,
                   COALESCE(pr.total_tests, 0) AS total_tests
            FROM tasks
            LEFT JOIN progress pr ON pr.task_id = tasks.id
                 AND pr.version = tasks.version AND pr.student_id = ?
            WHERE tasks.folder_id = ? AND tasks.project_id = ?
              AND tasks.challenge_stage IS NOT NULL AND {ACTIVE_TASK_FILTER}
            ORDER BY tasks.challenge_stage""",
        (NEW_STATUS, user["sub"], folder["id"], folder["project_id"]),
    ).fetchall()

    stages = [_stage(i, row) for i, row in enumerate(rows)]
    # The first stage the student has not passed yet is where «Начать» goes.
    current = next((s.number for s in stages if s.status != "passed"), 0)
    for stage in stages:
        stage.current = stage.number == current

    workspace = _workspace(folder["workspace_json"])
    return ChallengeDTO(
        id=folder["id"],
        project_id=folder["project_id"],
        code=folder["code"],
        name=folder["name"],
        description=folder["description"],
        order=folder["order"],
        level=folder["level"],
        theory=_theory(rows),
        workspace=workspace,
        stages=stages,
        starter=_starter_files(rows, workspace),
    )


def _stage(index: int, row) -> ChallengeStageDTO:
    """One ``tasks`` row as a stage; the number is ``challenge_stage``."""
    return ChallengeStageDTO(
        id=row["id"],
        title=row["title"],
        number=int(row["challenge_stage"]),
        order=index,
        level=row["level"],
        version=row["version"],
        status=row["status"],
        passed_tests=row["passed_tests"],
        total_tests=row["total_tests"],
    )


def _theory(rows) -> list[str]:
    """Lesson ids of the stages, in stage order, without repeats."""
    out: list[str] = []
    for row in rows:
        for lesson_id in json.loads(row["theory"] or "[]"):
            if lesson_id not in out:
                out.append(lesson_id)
    return out


def _workspace(raw: str | None) -> ChallengeWorkspaceDTO:
    """Stored ``workspace_json`` or the library defaults (``NULL`` = defaults)."""
    spec = json.loads(raw) if raw else {}
    try:
        return ChallengeWorkspaceDTO(**Workspace(**spec).model_dump())
    except (TypeError, ValueError):
        # A hand-edited folder.yaml must not break the endpoint: the stage
        # check validates the same spec again with Russian messages.
        return ChallengeWorkspaceDTO(
            entry=spec.get("entry") or DEFAULT_ENTRY, include=list(DEFAULT_INCLUDE)
        )


def _starter_files(rows, workspace: ChallengeWorkspaceDTO) -> dict[str, str]:
    """``{path: content}`` of the folder's ``starter/`` project (empty if none)."""
    if not rows:
        return {}
    # md_path is stored absolute by sync; the walker's relative fallback is
    # resolved the same way as for /tasks (see routers/tasks._resolve_md_path).
    folder_dir = _resolve_folder_dir(Path(rows[0]["md_path"]))
    starter = folder_dir / "starter"
    if not starter.is_dir():
        return {}
    return read_project_files(starter, workspace.include)


def _resolve_folder_dir(md_path: Path) -> Path:
    """Directory of a stage ``.md`` (absolute, or relative to the repo root)."""
    if md_path.is_absolute():
        return md_path.parent
    repo_root = Path(__file__).parent.parent.parent
    return (repo_root / md_path).parent
