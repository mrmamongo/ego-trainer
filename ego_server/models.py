"""Pydantic DTOs for API request/response bodies.

Бизнес-логика и полные модели — в задаче ego-trainer-bmh.2 (Auth) и далее.
Тут только минимальные схемы, чтобы роутеры компилировались.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = Field(default="student", pattern="^(student|mentor|admin)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    user_id: str


class MeResponse(BaseModel):
    user_id: str
    username: str
    role: str


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


class CheckRequest(BaseModel):
    """Request body for POST /check — run checker server-side."""

    task_id: str
    student_code: str


class TestResultDTO(BaseModel):
    """One test result in a CheckResponse."""

    description: str
    passed: bool
    expected_repr: str
    actual_repr: str | None = None
    error: str | None = None


class CheckResponse(BaseModel):
    """Response from POST /check — full check result."""

    task_id: str
    version: str
    status: str  # passed | partial | failed | error | timeout | no_tests
    passed_tests: int
    total_tests: int
    solution_hash: str
    results: list[TestResultDTO] = Field(default_factory=list)
    log: str  # human-readable summary


class Hint(BaseModel):
    """One progressive hint for a task."""

    level: int
    title: str
    content: str


class HintsResponse(BaseModel):
    """Progressive hints for a task (rules → example → signature)."""

    task_id: str
    hints: list[Hint] = Field(default_factory=list)
