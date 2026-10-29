"""Catalog models + YAML parsers — Project / Folder / Task hierarchy.

Per ADR-0016 D16.6: content-repo is a 3-level catalog.
Each level has its own YAML config; sync reads meta from there
(not from DB, not from git-tag alone).

Layout::

    ego-tasks/
    ├── catalog.yaml                 # list of projects (or one default)
    └── projects/
        └── <project_id>/
            ├── project.yaml
            └── folders/
                └── <folder_id>/
                    ├── folder.yaml
                    ├── lesson_<slug>.md          # theory card (optional)
                    ├── task_<slug>.md
                    ├── task_<slug>.solution.py
                    └── task_<slug>.tests.py

Legacy fixture (``docs/tasks/block_*/`` without YAML) imports as:
- project ``fixture`` (synthetic)
- folder = directory name (``block_f_simple``)
- task meta from H1 + bold lines; version default ``1.0.0`` +
  ``version_policy: auto_minor``
- lessons are ignored (legacy layout has none)
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from ego.models import Level

# === Enums as Literal ===

VersionPolicy = Literal["declare", "auto_minor"]
AuthType = Literal["none", "token", "ssh"]

#: Task ids and lesson ids become path segments in the content API
#: (``/tasks/<id>``, ``/lessons/<id>``); keep them URL-safe and shadow-proof.
#: The same pattern is used by the server to reject query params outright.
CONTENT_ID_RE = r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}"

# === Catalog root (catalog.yaml) ===


class CatalogEntry(BaseModel):
    """One row in ``catalog.yaml`` ``projects:`` list."""

    id: str
    path: str  # relative to repo root, e.g. "projects/junior-core"
    enabled: bool = True


class Catalog(BaseModel):
    """Parsed ``catalog.yaml`` — table of contents for the content-repo."""

    schema_version: int = 1
    projects: list[CatalogEntry] = Field(default_factory=list)


# === Project (project.yaml) ===


class RecommendedAfter(BaseModel):
    """Soft course recommendation (``project.yaml`` → ``recommended_after``).

    Advisory only: it never blocks a task or a project. ``min_passed`` is the
    number of passed tasks in ``project``; ``min_per_kind`` (optional) asks
    for at least N passed tasks per kind tag (``bug`` / ``modify`` / ``new``);
    ``note`` is a free-form sentence shown to the student.
    """

    model_config = ConfigDict(extra="ignore")

    project: str  # prerequisite project id
    min_passed: int = 0
    min_per_kind: int | None = None
    note: str = ""


class Project(BaseModel):
    """One course / track. Parsed from ``project.yaml``."""

    model_config = ConfigDict(extra="ignore")

    id: str  # stable id (= path slug)
    name: str
    description: str = ""
    version: str = "1.0.0"  # SemVer of the curriculum pack
    order: int = 0
    default_locale: str = "ru"
    tags: list[str] = Field(default_factory=list)
    version_policy: VersionPolicy = "declare"
    # Soft prerequisite for this course; never enforced.
    recommended_after: RecommendedAfter | None = None

    # Set by walker (not from YAML) — absolute path to project dir.
    path: Path | None = None


# === Folder (folder.yaml) ===


class Workspace(BaseModel):
    """File rules of a challenge project (``folder.yaml`` → ``workspace``).

    The student's whole project folder is checked (ADR-0018): ``entry`` is
    what the black-box run starts, ``include`` lists the files collected
    from the folder (``*.py`` matches every directory, ``data/*.json`` only
    that path), ``max_files`` / ``max_bytes`` cap a submission.
    """

    model_config = ConfigDict(extra="ignore")

    entry: str = "main.py"
    include: list[str] = Field(default_factory=lambda: ["*.py"])
    max_files: int = Field(default=20, ge=1)
    max_bytes: int = Field(default=200_000, ge=1)


class Folder(BaseModel):
    """Thematic block inside a project (former ``block_*``).

    ``kind: challenge`` marks a multi-file challenge: its ``stage_NN_*.md``
    files are the stages, ``starter/`` is the starting project and
    ``solution/`` the reference (ADR-0018 D18.1). Ordinary folders keep
    ``task_*.md`` files and leave ``workspace`` unset.
    """

    model_config = ConfigDict(extra="ignore")

    id: str  # stable id (directory slug)
    code: str  # short block code: 'F', '1', 'A', ...
    name: str
    description: str = ""
    order: int = 0
    level: Level | None = None  # easy | medium | hard (optional)
    kind: Literal["tasks", "challenge"] = "tasks"
    # Only for challenges; ``None`` elsewhere (defaults: ego.runner).
    workspace: Workspace | None = None

    # Set by walker (not from YAML).
    path: Path | None = None
    project_id: str | None = None

    @property
    def is_challenge(self) -> bool:
        """True for a challenge folder (stages instead of single-file tasks)."""
        return self.kind == "challenge"


# === Task frontmatter (YAML inside .md) ===


class TaskFrontmatter(BaseModel):
    """YAML frontmatter at the top of ``task_*.md``.

    Source of truth for sync (per D16.6). Body of ``.md`` = statement;
    solution/tests = sidecars (``.solution.py`` / ``.tests.py``).
    """

    model_config = ConfigDict(extra="ignore")

    id: str  # 'F1', '1.5', 'A', ...
    title: str
    version: str = "1.0.0"  # SemVer of the task (D3)
    level: Level = "easy"
    tags: list[str] = Field(default_factory=list)
    folder: str | None = None  # optional; default = parent dirname
    breaking: bool = False
    # Ordered lesson ids (theory cards) shown before the task. Not part of
    # the grading content: sync refreshes it even when the hash is unchanged.
    theory: list[str] = Field(default_factory=list)


# === Lesson frontmatter (YAML inside ``lesson_*.md``) ===


class LessonFrontmatter(BaseModel):
    """YAML frontmatter at the top of ``lesson_*.md`` (theory card).

    Lessons are folder-level Markdown cards; they have no solution/tests
    and are never graded. Body of ``.md`` = lesson content (``body_md``).
    """

    model_config = ConfigDict(extra="ignore")

    id: str  # unique across the whole content-repo
    title: str = ""
    order: int = 0  # sort inside folder
    version: str = "1.0.0"  # informational (no SemVer enforcement)


# === Parsers ===


def parse_catalog(text: str) -> Catalog:
    """Parse ``catalog.yaml`` text into :class:`Catalog`.

    Raises ``ValueError`` if YAML is invalid or schema_version is unsupported.
    """
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError("catalog.yaml must be a mapping")
    schema_version = data.get("schema_version", 1)
    if schema_version != 1:
        raise ValueError(f"Unsupported catalog schema_version: {schema_version}")
    projects_raw = data.get("projects", []) or []
    entries = [CatalogEntry(**p) for p in projects_raw]
    return Catalog(schema_version=schema_version, projects=entries)


def parse_project(text: str) -> Project:
    """Parse ``project.yaml`` text into :class:`Project`."""
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError("project.yaml must be a mapping")
    return Project(**data)


def parse_folder(text: str) -> Folder:
    """Parse ``folder.yaml`` text into :class:`Folder`."""
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError("folder.yaml must be a mapping")
    return Folder(**data)


# === Frontmatter extraction (YAML block at top of .md) ===

_FM_DELIM = "---"
_FM_RE_MAX_LINES = 200  # safety: frontmatter must be in first 200 lines


def split_frontmatter(md_text: str) -> tuple[dict | None, str]:
    """Split ``---\\n...\\n---\\n<body>`` into ``(frontmatter_dict, body)``.

    Returns ``(None, md_text)`` if no frontmatter present.
    Raises ``ValueError`` if delimiter found but YAML block is malformed.

    Per ADR-0016 D16.6: frontmatter is the source of truth for sync meta.
    """
    lines = md_text.splitlines()
    if not lines or lines[0].strip() != _FM_DELIM:
        return None, md_text

    # Find closing delimiter (line 1..N).
    for i in range(1, min(len(lines), _FM_RE_MAX_LINES)):
        if lines[i].strip() == _FM_DELIM:
            fm_text = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :]).lstrip("\n")
            try:
                data = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid frontmatter YAML: {e}") from e
            if not isinstance(data, dict):
                raise ValueError("frontmatter must be a mapping")
            return data, body

    raise ValueError("Unclosed frontmatter (no closing '---' found)")


def parse_task_frontmatter(md_text: str) -> tuple[TaskFrontmatter | None, str]:
    """Parse ``task_*.md`` → ``(TaskFrontmatter | None, body_md)``.

    If no frontmatter present, returns ``(None, md_text)`` — caller may
    fall back to legacy H1/bold parsing.
    """
    fm_dict, body = split_frontmatter(md_text)
    if fm_dict is None:
        return None, body
    return TaskFrontmatter(**fm_dict), body


def parse_lesson_frontmatter(md_text: str) -> tuple[LessonFrontmatter, str]:
    """Parse ``lesson_*.md`` → ``(LessonFrontmatter, body_md)``.

    Raises ``ValueError`` when frontmatter is missing, malformed or has no
    ``id``. ``title`` defaults to the first body H1 (``# ...``) if omitted.
    """
    fm_dict, body = split_frontmatter(md_text)
    if fm_dict is None:
        raise ValueError("lesson must start with YAML frontmatter (--- ... ---)")
    fm = LessonFrontmatter(**fm_dict)
    if not fm.title:
        fm.title = _first_h1(body) or fm.id
    return fm, body


def lesson_content_hash(fm: LessonFrontmatter, body: str) -> str:
    """sha256 over lesson meta + body (markdown text → hex digest).

    Uses the same null-byte separators as :func:`ego.parser._hash_content`.
    """
    parts = (fm.id, fm.title, str(fm.order), fm.version, body)
    return hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()


def _first_h1(body: str) -> str:
    """First ``# Title`` line of ``body`` (empty string if absent)."""
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


# === File-level convenience ===


def load_catalog(repo_root: Path) -> Catalog:
    """Load ``catalog.yaml`` from repo root. Returns empty Catalog if missing.

    Per D16.6: a content-repo without ``catalog.yaml`` is treated as
    having a single implicit project ``fixture`` (legacy compatibility).
    """
    path = repo_root / "catalog.yaml"
    if not path.is_file():
        return Catalog()
    return parse_catalog(path.read_text(encoding="utf-8"))


def load_project_file(path: Path) -> Project:
    """Load ``project.yaml`` from disk."""
    return parse_project(path.read_text(encoding="utf-8"))


def load_folder_file(path: Path) -> Folder:
    """Load ``folder.yaml`` from disk."""
    return parse_folder(path.read_text(encoding="utf-8"))
