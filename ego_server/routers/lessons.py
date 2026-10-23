"""Lessons router — GET /lessons (list), GET /lessons/<id> (with body_md).

Theory cards (``lesson_*.md`` in a catalog folder) shown to students before
the tasks that reference them via ``theory: [<lesson id>, ...]``.

Per ADR-0016 catalog visibility: a lesson is visible only when its project
is visible (not archived), matching :data:`ego_server.catalog_visibility.
ACTIVE_TASK_FILTER` for tasks. ``block`` = folder ``code``, the same value
that ``TaskMeta.block`` carries for tasks of that folder.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from ego.catalog import CONTENT_ID_RE
from ego_server.catalog_visibility import ACTIVE_LESSON_FILTER
from ego_server.deps import CurrentUser, DbDep
from ego_server.models import LessonFull, LessonMeta


router = APIRouter()

#: Lessons + their folder code (the block students see), joined through the
#: catalog so a lesson whose project/folder vanished is never visible.
_LESSONS_SQL = """SELECT lessons.id, lessons.project_id, lessons.folder_id,
        f.code AS block, lessons.title, lessons."order" AS lorder,
        lessons.version, lessons.content_hash, lessons.body_md
    FROM lessons
    JOIN projects p ON p.id = lessons.project_id
    JOIN folders f ON f.id = lessons.folder_id AND f.project_id = lessons.project_id"""

_LESSONS_ORDER = 'ORDER BY p."order", f."order", lessons."order", lessons.id'


@router.get("", response_model=list[LessonMeta])
async def list_lessons(
    db: DbDep,
    user: CurrentUser,
    folder_id: Annotated[str | None, Query(description="Filter by folder id")] = None,
) -> list[LessonMeta]:
    """List visible lessons (metadata only). Optional ?folder_id=<id> filter."""
    where = ACTIVE_LESSON_FILTER + (" AND lessons.folder_id = ?" if folder_id else "")
    rows = db.execute(
        f"{_LESSONS_SQL} WHERE {where} {_LESSONS_ORDER}",
        (folder_id,) if folder_id else (),
    ).fetchall()
    return [_row_to_meta(r) for r in rows]


@router.get("/{lesson_id}", response_model=LessonFull)
async def get_lesson(
    db: DbDep,
    user: CurrentUser,
    lesson_id: Annotated[str, Path(pattern=f"^{CONTENT_ID_RE}$")],
) -> LessonFull:
    """Get one lesson with its markdown body. 404 if unknown or hidden."""
    row = db.execute(
        f"{_LESSONS_SQL} WHERE lessons.id = ? AND {ACTIVE_LESSON_FILTER}",
        (lesson_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson '{lesson_id}' not found",
        )
    return LessonFull(
        **_row_to_meta(row).model_dump(),
        body_md=row["body_md"] or "",
    )


# === Helpers ===


def _row_to_meta(row) -> LessonMeta:
    return LessonMeta(
        id=row["id"],
        project_id=row["project_id"],
        folder_id=row["folder_id"],
        block=row["block"],
        title=row["title"],
        order=row["lorder"],
        version=row["version"],
        content_hash=row["content_hash"],
    )
