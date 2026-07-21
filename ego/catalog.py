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
                    ├── task_<slug>.md
                    ├── task_<slug>.solution.py
                    └── task_<slug>.tests.py

Legacy fixture (``docs/tasks/block_*/`` without YAML) imports as:
- project ``fixture`` (synthetic)
- folder = directory name (``block_f_simple``)
- task meta from H1 + bold lines; version default ``1.0.0`` +
  ``version_policy: auto_minor``
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from ego.models import Level

# === Enums as Literal ===

VersionPolicy = Literal["declare", "auto_minor"]
AuthType = Literal["none", "token", "ssh"]

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

    # Set by walker (not from YAML) — absolute path to project dir.
    path: Path | None = None


# === Folder (folder.yaml) ===


class Folder(BaseModel):
    """Thematic block inside a project (former ``block_*``)."""

    model_config = ConfigDict(extra="ignore")

    id: str  # stable id (directory slug)
    code: str  # short block code: 'F', '1', 'A', ...
    name: str
    description: str = ""
    order: int = 0
    level: Level | None = None  # easy | medium | hard (optional)

    # Set by walker (not from YAML).
    path: Path | None = None
    project_id: str | None = None


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
