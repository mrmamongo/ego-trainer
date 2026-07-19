"""Tasks router — реализация в задаче ego-trainer-bmh.3.

Сейчас заглушки, возвращающие 501.
"""

from fastapi import APIRouter, HTTPException, status

from ego_server.models import TaskFull, TaskMeta


router = APIRouter()


@router.get("", response_model=list[TaskMeta])
async def list_tasks() -> list[TaskMeta]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="tasks implemented in bmh.3",
    )


@router.get("/{task_id}", response_model=TaskFull)
async def get_task(task_id: str) -> TaskFull:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="tasks implemented in bmh.3",
    )
