"""Projects router — GET /projects (soft recommendations for the current user).

Each project reports the ``recommended_after`` declared in its
``project.yaml`` (stored by sync) and the current student's ``readiness``
against it. Readiness is informational: it never blocks anything.
"""

from __future__ import annotations

from fastapi import APIRouter

from ego_server.deps import CurrentUser, DbDep
from ego_server.models import ProjectDTO
from ego_server.recommendations import list_projects


router = APIRouter()


@router.get("", response_model=list[ProjectDTO])
async def get_projects(db: DbDep, user: CurrentUser) -> list[ProjectDTO]:
    """Visible projects with ``recommended_after`` + readiness of the caller."""
    return [ProjectDTO(**row) for row in list_projects(db, user["sub"])]
