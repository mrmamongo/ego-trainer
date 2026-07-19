"""Progress router — реализация в задачах bmh.4 (push) и bmh.5 (get).

Сейчас заглушки, возвращающие 501.
"""

from fastapi import APIRouter, HTTPException, status

from ego_server.deps import CurrentUser
from ego_server.models import ProgressPush, ProgressRow


router = APIRouter()


@router.post("/push", response_model=ProgressRow)
async def push_progress(body: ProgressPush, user: CurrentUser) -> ProgressRow:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="push implemented in bmh.4",
    )


@router.get("/{student_id}", response_model=list[ProgressRow])
async def get_progress(student_id: str, user: CurrentUser) -> list[ProgressRow]:
    # В реальной реализации — require_role("mentor", "admin")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="get implemented in bmh.5",
    )
