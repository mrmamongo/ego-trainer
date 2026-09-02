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


# === Content-repo sync (ADR-0016) ===


class SyncTasksRequest(BaseModel):
    """Request body for POST /admin/sync-tasks (PR 1: local path only)."""

    path: str  # local filesystem path or file:// URL
    source: str = Field(default="manual", pattern="^(manual|cron|startup)$")


class SyncResultDTO(BaseModel):
    """Result of one sync run."""

    log_id: int
    status: str  # success | partial | failed
    added: int
    updated: int
    skipped: int
    errors: int
    error_details: str = ""
    started_at: str
    finished_at: str = ""
    git_sha: str | None = None
    repo_url: str = ""


class SyncLogRow(BaseModel):
    """One row from sync_log (GET /admin/sync/log)."""

    id: int
    started_at: str
    finished_at: str | None = None
    source: str
    repo_url: str = ""
    git_sha: str | None = None
    status: str
    added: int
    updated: int
    skipped: int
    errors: int
    error_details: str = ""


# === Admin panel ===


class StudentSummaryDTO(BaseModel):
    """Summary of one student for the admin panel (GET /admin/students)."""

    student_id: str
    username: str
    role: str
    tasks_total: int
    tasks_passed: int
    tasks_partial: int
    tasks_failed: int
    last_activity: str | None = None


class CreateUserRequest(BaseModel):
    """Request body for POST /admin/users (create user)."""

    username: str
    password: str
    role: str = Field(pattern="^(student|mentor|admin)$")


class UpdateRoleRequest(BaseModel):
    """Request body for PUT /admin/users/<id>/role."""

    role: str = Field(pattern="^(student|mentor|admin)$")


class ResetPasswordRequest(BaseModel):
    """Request body for PUT /admin/users/<id>/password."""

    password: str = Field(min_length=1)


class OverviewCounts(BaseModel):
    """Row counts for the overview snapshot (GET /admin/overview)."""

    projects: int
    folders: int
    tasks: int
    students: int


class OverviewDTO(BaseModel):
    """Aggregate snapshot for GET /admin/overview (mentor/admin only).

    ``server`` is a stable status string (currently always ``"ok"`` — the
    endpoint itself would not be reachable if the server were down).
    Counts reflect the current DB state. ``latest_sync`` is the most recent
    ``sync_log`` row or ``None`` when no sync has ever run.
    """

    server: str = "ok"
    counts: OverviewCounts
    latest_sync: SyncLogRow | None = None


# === Catalog browse (GET /admin/catalog) ===


class CatalogTaskDTO(BaseModel):
    """One task in the catalog hierarchy (GET /admin/catalog).

    Only columns that exist on the ``tasks`` table are exposed — no
    invented schema. ``breaking`` is normalised to a bool from the 0/1 int.
    """

    id: str
    task_id: str
    title: str
    block: str
    slug: str
    level: str
    version: str
    breaking: bool = False
    md_path: str
    folder_id: str | None = None
    project_id: str | None = None


class CatalogFolderDTO(BaseModel):
    """One folder in the catalog hierarchy (GET /admin/catalog)."""

    id: str
    project_id: str
    code: str
    name: str
    order: int
    level: str | None = None
    tasks: list[CatalogTaskDTO] = Field(default_factory=list)


class CatalogProjectDTO(BaseModel):
    """One project in the catalog hierarchy (GET /admin/catalog)."""

    id: str
    name: str
    order: int
    version: str
    folders: list[CatalogFolderDTO] = Field(default_factory=list)


class CatalogDTO(BaseModel):
    """Full catalog hierarchy for GET /admin/catalog (mentor/admin only).

    ``projects`` is ordered by (``order``, ``id``); folders by
    (``order``, ``id``); tasks by (``task_id``, ``id``). When ``q`` is
    supplied, unmatched leaves are pruned but ancestors of matches are
    retained. An empty DB yields ``{"projects": []}``.
    """

    projects: list[CatalogProjectDTO] = Field(default_factory=list)


# === Task Studio read (GET /admin/tasks/{task_id}/studio) ===


class TaskStudioDTO(BaseModel):
    """Canonical task content for the Task Studio read view.

    Content (``markdown`` / ``solution_py`` / ``tests_py``) is read
    directly from the configured local content-repo root — never from
    SQLite blobs. ``writable`` is ``False`` with a concise
    ``read_only_reason`` when the repo is unconfigured/non-local/
    missing/unwritable, or when any resolved task/sidecar path escapes
    the canonical root via ``..`` or a symlink. When content cannot be
    read safely, the string fields are empty and only the DB identity
    metadata is returned.
    """

    task_id: str
    version: str
    md_path: str
    markdown: str = ""
    solution_py: str = ""
    tests_py: str = ""
    writable: bool = False
    read_only_reason: str = ""


# === Task Studio validate (POST /admin/tasks/{task_id}/studio/validate) ===


class StudioValidateRequest(BaseModel):
    """Request body for POST /admin/tasks/{task_id}/studio/validate.

    The candidate is validated entirely in-memory — no canonical files are
    modified. ``expected_version`` must match the current DB version of the
    task (optimistic concurrency); a mismatch yields 409.
    """

    expected_version: str
    markdown: str  # full .md including YAML frontmatter
    solution_py: str
    tests_py: str = ""


class StudioValidateResponse(BaseModel):
    """Success response for POST /admin/tasks/{task_id}/studio/validate.

    Returned only when the candidate passes all validation checks. The
    canonical files are guaranteed byte-identical (validation never writes
    to the content repo — the candidate is parsed from a temp directory).
    """

    valid: bool = True
    task_id: str
    current_version: str
    candidate_version: str
    content_changed: bool
    version_policy: str
