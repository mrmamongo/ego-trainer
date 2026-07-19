"""Tasks router — GET /tasks (list), GET /tasks/<id> (full).

Per ADR-0001 D2 (git canonical), D4 (solution cached locally after pull),
D8 (JWT + roles):
- Students see TaskFull without solution_py on /tasks/<id>
- Mentors/admins see full TaskFull with solution_py via ?include_solution=true
- All roles can list tasks
- GET /tasks/<id>/solution is mentors/admins only (403 for students)
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ego_server.db_helpers import get_task_meta
from ego_server.deps import CurrentUser, DbDep, require_role
from ego_server.models import Hint, HintsResponse, TaskFull, TaskMeta


router = APIRouter()


@router.get("", response_model=list[TaskMeta])
async def list_tasks(
    db: DbDep,
    user: CurrentUser,
    block: Annotated[str | None, Query(description="Filter by block letter")] = None,
) -> list[TaskMeta]:
    """List all tasks (metadata only, no content). Optional ?block=F filter."""
    if block:
        rows = db.execute(
            "SELECT id, block, slug, task_id, title, level, tags, version, "
            "content_hash, breaking, md_path FROM tasks WHERE block = ? "
            "ORDER BY block, task_id",
            (block,),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT id, block, slug, task_id, title, level, tags, version, "
            "content_hash, breaking, md_path FROM tasks ORDER BY block, task_id"
        ).fetchall()
    return [_row_to_meta(r) for r in rows]


@router.get("/{task_id}", response_model=TaskFull)
async def get_task(
    task_id: str,
    db: DbDep,
    user: CurrentUser,
    include_solution: Annotated[
        bool, Query(description="Include solution_py (mentors/admins only)")
    ] = False,
) -> TaskFull:
    """Get full task by id. By default solution_py is empty (hidden from students).

    Query params:
        include_solution=true — return solution_py. Only mentors/admins;
        silently ignored for students (they get empty solution_py).
    """
    meta = get_task_meta(db, task_id)
    if meta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    md_path_str = meta["md_path"]
    path = _resolve_md_path(md_path_str)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task .md file not found at {md_path_str}",
        )

    from ego.parser import parse_task_file

    task = parse_task_file(path)

    can_see_solution = include_solution and user["role"] in ("mentor", "admin")

    return TaskFull(
        id=task.id,
        block=task.block,
        slug=task.slug,
        task_id=task.task_id,
        title=task.title,
        level=task.level,
        tags=task.tags,
        version=meta["version"],  # DB version (may have been bumped)
        content_hash=task.content_hash,
        breaking=meta["breaking"],
        md_path=str(task.md_path),
        statement_md=task.statement_md,
        stub_py=task.stub_py,
        solution_py=task.solution_py if can_see_solution else "",
    )


@router.get("/{task_id}/solution", response_model=dict)
async def get_task_solution(
    task_id: str,
    db: DbDep,
    user: Annotated[dict, Depends(require_role("mentor", "admin"))],
) -> dict:
    """Get only the solution_py for a task. Mentors/admins only."""
    meta = get_task_meta(db, task_id)
    if meta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    path = _resolve_md_path(meta["md_path"])
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task .md file not found at {meta['md_path']}",
        )

    from ego.parser import parse_task_file

    task = parse_task_file(path)
    return {
        "task_id": task_id,
        "solution_py": task.solution_py,
        "version": meta["version"],
    }


@router.get("/{task_id}/hints", response_model=HintsResponse)
async def get_task_hints(
    task_id: str,
    db: DbDep,
    user: CurrentUser,
    level: Annotated[int | None, Query(description="Max hint level (1=rules, 2=example, 3=signature)")] = None,
) -> HintsResponse:
    """Get progressive hints for a task.

    Levels:
        1. Rules (## Правила section from .md)
        2. Example (## Пример section from .md)
        3. Function signature (from stub_py)

    Pass ?level=N to get only hints up to level N.
    """
    meta = get_task_meta(db, task_id)
    if meta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    path = _resolve_md_path(meta["md_path"])
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task .md file not found at {meta['md_path']}",
        )

    from ego.parser import parse_task_file

    task = parse_task_file(path)

    hints: list[Hint] = []
    max_level = level or 3

    # Level 1: Rules from statement_md.
    if max_level >= 1:
        rules = _extract_section(task.statement_md, "Правила")
        if rules:
            hints.append(Hint(level=1, title="Правила", content=rules))

    # Level 2: Example from statement_md.
    if max_level >= 2:
        example = _extract_section(task.statement_md, "Пример")
        if example:
            hints.append(Hint(level=2, title="Пример", content=example))

    # Level 3: Function signature from stub.
    if max_level >= 3:
        sig = _extract_signature(task.stub_py)
        if sig:
            hints.append(
                Hint(
                    level=3,
                    title="Сигнатура функции",
                    content=f"```python\n{sig}\n```",
                )
            )

    return HintsResponse(task_id=task_id, hints=hints)


# === Helpers ===


def _extract_section(md: str, section_name: str) -> str:
    """Extract a ## section from markdown text."""
    lines = md.split("\n")
    capturing = False
    result: list[str] = []
    for line in lines:
        if line.strip().startswith("## ") and section_name in line:
            capturing = True
            continue
        if capturing and line.strip().startswith("## "):
            break
        if capturing:
            result.append(line)
    return "\n".join(result).strip()


def _extract_signature(stub_py: str) -> str:
    """Extract the function signature from stub code."""
    for line in stub_py.split("\n"):
        if line.strip().startswith("def task_"):
            return line.strip().rstrip(":")
    return ""


def _resolve_md_path(md_path_str: str) -> Path:
    """Resolve a stored md_path (may be relative) to an existing file.

    Tries: as-is (cwd-relative), then relative to the repo root
    (parent of ego_server/).
    """
    path = Path(md_path_str)
    if path.is_absolute():
        return path
    if path.exists():
        return path
    # Try relative to repo root (parent of ego_server/).
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / md_path_str


def _row_to_meta(row) -> TaskMeta:
    import json

    return TaskMeta(
        id=row["id"],
        block=row["block"],
        slug=row["slug"],
        task_id=row["task_id"],
        title=row["title"],
        level=row["level"],
        tags=json.loads(row["tags"]) if row["tags"] else [],
        version=row["version"],
        content_hash=row["content_hash"],
        breaking=bool(row["breaking"]),
        md_path=row["md_path"],
    )
