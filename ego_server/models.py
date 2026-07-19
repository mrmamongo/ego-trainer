"""Pydantic DTOs for API request/response bodies.

Бизнес-логика и полные модели — в задаче ego-trainer-bmh.2 (Auth) и далее.
Тут только минимальные схемы, чтобы роутеры компилировались.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class TaskMeta(BaseModel):
    """Метаданные задачи (без контента — контент в git .md)."""
    id: str
    block: str
    slug: str
    task_id: str
    title: str
    level: str
    tags: list[str] = Field(default_factory=list)
    version: str
    content_hash: str
    breaking: bool = False
    md_path: str


class TaskFull(TaskMeta):
    """Задача с контентом (отдаётся по GET /tasks/<id>)."""
    statement_md: str
    stub_py: str
    solution_py: str


class ProgressPush(BaseModel):
    """Push прогресса от студента."""
    task_id: str
    version: str
    solution_hash: str
    status: str  # 'passed' | 'failed' | 'error' | 'timeout'
    log: str
    passed_tests: int = 0
    total_tests: int = 0


class ProgressRow(BaseModel):
    student_id: str
    task_id: str
    version: str
    status: str
    attempts: int
    passed_tests: int
    total_tests: int
    last_run_at: str | None = None
