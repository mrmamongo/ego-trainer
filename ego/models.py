"""Pydantic v2 data models — foundation of the ego platform.

These models are the single source of truth shared across all layers:
the parser returns ``Task``, the runner/checker consume it, the CLI/TUI
display it, the server stores ``Manifest``/``Progress``/``Config``/``Run``.

Implemented in task ego-trainer-93h.2 (Foundation epic).

Design notes (see ADR-0001):
- Pydantic v2 style: ``BaseModel``, ``Field(default_factory=...)``, ``ConfigDict``.
- ``pathlib.Path`` for ``md_path`` — Pydantic serializes it to ``str`` in JSON.
- ``datetime`` — ISO 8601, parsed/serialized by Pydantic automatically.
- ``Literal`` for enum-like fields (not ``Enum`` classes) — friendlier for JSON.
- Models are NOT frozen: we mutate ``Progress`` in place via ``upsert``.
- ``Manifest`` / ``Progress`` / ``Config`` are root models for ``.ego/`` files.
- ``Task`` is what the parser returns; it is not stored in ``.ego/`` directly
  (only referenced through ``Manifest``).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# === Level / Status enums as Literal ===

Level = Literal["easy", "medium", "hard"]
TaskStatus = Literal["new", "partial", "passed", "stale"]
RunStatus = Literal["passed", "failed", "error", "timeout"]
Role = Literal["student", "mentor", "admin"]


# === Task content (результат парсинга .md) ===


class Task(BaseModel):
    """Одна задача: условие + эталон + meta. Результат ego.parser.parse_task_file()."""

    model_config = ConfigDict(frozen=False)

    id: str  # 'F1', '1.5', 'A', 'H8', etc.
    block: str  # 'F', '1', 'A', 'H', ...
    slug: str  # 'block_f_simple'
    task_id: str  # = id (дублируется для удобства API)
    title: str
    level: Level
    tags: list[str] = Field(default_factory=list)
    version: str = "1.0.0"  # SemVer
    content_hash: str = ""  # sha256(statement_md + stub_py + solution_py), hex
    md_path: Path  # путь к .md файлу

    # Контент (см. ADR D2 — git canonical, .md как источник)
    statement_md: str  # markdown условия (без эталона)
    stub_py: str  # заготовка с `pass` для студента
    solution_py: str  # эталон (скрыт от TUI)

    # Опц. — если в .md были тестовые данные (пока почти никогда)
    extra: dict = Field(default_factory=dict)


# === Manifest (.ego/manifest.yaml) ===


class ManifestTaskEntry(BaseModel):
    """Одна строка в manifest.yaml — что выгружено на клиент."""

    id: str
    block: str
    slug: str
    version: str  # SemVer на момент pull
    content_hash: str
    pulled_at: datetime
    md_path: str  # путь к .md в tasks/ на клиенте

    # Локальные правки студента
    md_modified: bool = False  # студент правил .md?
    stub_modified: bool = False  # студент правил stub.py (не решение)?


class Manifest(BaseModel):
    """.ego/manifest.yaml — что выгружено и какие версии."""

    tasks: list[ManifestTaskEntry] = Field(default_factory=list)
    server_version: str = ""  # SemVer сервера при последнем pull
    last_pull_at: datetime | None = None


# === Progress (.ego/progress.json) ===


class ProgressEntry(BaseModel):
    """Прогресс по одной задаче (per-version)."""

    task_id: str
    version: str  # на какой версии сдавал
    status: TaskStatus = "new"
    attempts: int = 0
    passed_tests: int = 0
    total_tests: int = 0
    last_run_at: datetime | None = None
    solution_hash: str = ""  # sha256 последнего решения


class Progress(BaseModel):
    """.ego/progress.json — весь прогресс студента."""

    student_id: str = ""
    student_username: str = ""
    entries: list[ProgressEntry] = Field(default_factory=list)

    def find(self, task_id: str, version: str) -> ProgressEntry | None:
        """Найти запись по (task_id, version)."""
        for e in self.entries:
            if e.task_id == task_id and e.version == version:
                return e
        return None

    def upsert(self, entry: ProgressEntry) -> None:
        """Вставить или обновить запись."""
        for i, e in enumerate(self.entries):
            if e.task_id == entry.task_id and e.version == entry.version:
                self.entries[i] = entry
                return
        self.entries.append(entry)


# === Run (один прогон check) ===


class Run(BaseModel):
    """Один запуск ego check — лог + результат. Пишется в .ego/runs/."""

    id: str  # UUID
    task_id: str
    version: str
    started_at: datetime
    finished_at: datetime | None = None
    status: RunStatus
    passed_tests: int = 0
    total_tests: int = 0
    solution_hash: str = ""
    log: str = ""  # stdout+stderr, обрезано
    error: str = ""  # traceback если упало


# === Config (.ego/config.yaml) ===


class Config(BaseModel):
    """.ego/config.yaml — конфиг клиента."""

    server_url: str = "http://localhost:8000"
    token: str = ""  # JWT
    student_id: str = ""
    student_username: str = ""
    role: Role = "student"
    sandbox_timeout_sec: float = 5.0
    sandbox_block_network: bool = True
    log_truncate_to: int = 8 * 1024
