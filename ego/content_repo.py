"""Content-repo walker — discover Project / Folder / Task from disk.

Per ADR-0016:
- D16.1: canonical = separate git repo with ``projects/<id>/folders/<id>/``
- D16.5: local dev uses ``file://`` URL or legacy ``docs/tasks/block_*/``
- D16.6: 3-level hierarchy with YAML configs

This module walks a content-repo directory and yields a structured
catalog: list of :class:`DiscoveredProject` (each with folders and task
file paths). It does NOT parse ``.md`` into :class:`ego.models.Task` —
that's the job of :mod:`ego.parser`. The walker only discovers layout
and meta (Project/Folder/TaskFrontmatter).

Two modes:

1. **Catalog mode** (new layout): repo has ``catalog.yaml`` +
   ``projects/<id>/project.yaml`` + ``folders/<id>/folder.yaml`` +
   ``task_*.md`` with YAML frontmatter.

2. **Legacy fixture mode** (``docs/tasks/block_*/`` without YAML):
   synthetic project ``fixture``, folder = directory name, task meta
   from H1 + bold lines (delegated to :mod:`ego.parser`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ego.catalog import (
    Catalog,
    Folder,
    Project,
    TaskFrontmatter,
    load_catalog,
    load_folder_file,
    load_project_file,
    parse_task_frontmatter,
)

# === Discovered structures ===

FIXTURE_PROJECT_ID = "fixture"
FIXTURE_PROJECT_NAME = "Fixture (legacy docs/tasks)"


@dataclass
class DiscoveredTask:
    """One task file on disk + parsed frontmatter (if any)."""

    md_path: Path
    frontmatter: TaskFrontmatter | None  # None = legacy, fall back to parser
    solution_path: Path | None  # <slug>.solution.py next to .md
    tests_path: Path | None  # <slug>.tests.py next to .md
    folder_id: str  # parent folder id (slug)
    project_id: str  # parent project id


@dataclass
class DiscoveredFolder:
    """One folder (block) with its meta and discovered tasks."""

    folder: Folder
    tasks: list[DiscoveredTask] = field(default_factory=list)


@dataclass
class DiscoveredProject:
    """One project with its meta and discovered folders."""

    project: Project
    folders: list[DiscoveredFolder] = field(default_factory=list)


@dataclass
class DiscoveredCatalog:
    """Full result of walking a content-repo."""

    projects: list[DiscoveredProject] = field(default_factory=list)
    is_legacy: bool = False  # True = no catalog.yaml, synthetic fixture

    @property
    def all_tasks(self) -> list[DiscoveredTask]:
        """Flatten all discovered tasks across projects/folders."""
        return [t for p in self.projects for f in p.folders for t in f.tasks]


# === Public API ===


def discover_repo(repo_root: Path) -> DiscoveredCatalog:
    """Walk a content-repo directory and return the discovered catalog.

    Auto-detects mode:
    - If ``catalog.yaml`` exists → catalog mode (D16.6 new layout).
    - Otherwise → legacy fixture mode (synthetic ``fixture`` project).

    Args:
        repo_root: path to content-repo root (or ``docs/tasks/`` for legacy).

    Returns:
        :class:`DiscoveredCatalog` with all projects/folders/tasks found.
    """
    repo_root = Path(repo_root)
    if not repo_root.is_dir():
        raise FileNotFoundError(f"repo root not found: {repo_root}")

    catalog = load_catalog(repo_root)
    if catalog.projects:
        return _discover_catalog_mode(repo_root, catalog)
    # No catalog.yaml → check if it looks like legacy block_* layout.
    return _discover_legacy_mode(repo_root)


# === Catalog mode (new layout) ===


def _discover_catalog_mode(
    repo_root: Path, catalog: Catalog
) -> DiscoveredCatalog:
    """Discover projects/folders/tasks per ``catalog.yaml``."""
    result = DiscoveredCatalog(is_legacy=False)
    for entry in catalog.projects:
        if not entry.enabled:
            continue
        proj_dir = (repo_root / entry.path).resolve()
        if not proj_dir.is_dir():
            continue  # missing project dir — skip silently
        proj = _load_project_or_synthetic(proj_dir, entry.id)
        proj.path = proj_dir
        dp = DiscoveredProject(project=proj)
        dp.folders = _discover_folders(proj_dir, proj.id)
        result.projects.append(dp)
    return result


def _load_project_or_synthetic(proj_dir: Path, project_id: str) -> Project:
    """Load ``project.yaml`` or build a synthetic Project from directory."""
    py = proj_dir / "project.yaml"
    if py.is_file():
        return load_project_file(py)
    # No project.yaml — synthesize from directory name.
    return Project(
        id=project_id,
        name=proj_dir.name.replace("_", " ").title(),
        description="",
        version="1.0.0",
        version_policy="auto_minor",
    )


def _discover_folders(proj_dir: Path, project_id: str) -> list[DiscoveredFolder]:
    """Walk ``proj_dir/folders/*/`` and discover folders + tasks."""
    folders_dir = proj_dir / "folders"
    if not folders_dir.is_dir():
        return []
    out: list[DiscoveredFolder] = []
    for folder_dir in sorted(folders_dir.iterdir()):
        if not folder_dir.is_dir():
            continue
        folder = _load_folder_or_synthetic(folder_dir)
        folder.path = folder_dir
        folder.project_id = project_id
        df = DiscoveredFolder(folder=folder)
        df.tasks = _discover_tasks(folder_dir, folder.id, project_id)
        out.append(df)
    return out


def _load_folder_or_synthetic(folder_dir: Path) -> Folder:
    """Load ``folder.yaml`` or build a synthetic Folder from directory."""
    fy = folder_dir / "folder.yaml"
    if fy.is_file():
        return load_folder_file(fy)
    # No folder.yaml — synthesize from directory name (e.g. block_f_simple).
    name = folder_dir.name
    # Try to extract short code: 'block_f_simple' -> 'F', 'block_1_logs' -> '1'
    code = _guess_code_from_dirname(name)
    return Folder(
        id=name,
        code=code,
        name=name.replace("_", " ").title(),
        description="",
    )


def _guess_code_from_dirname(name: str) -> str:
    """Extract short block code from directory name.

    ``block_f_simple`` → ``F``, ``block_1_logs`` → ``1``, ``block_a_join`` → ``A``.
    Falls back to uppercased first char of the name.
    """
    parts = name.split("_")
    if len(parts) >= 2 and parts[0] == "block":
        return parts[1].upper()
    return name[:1].upper() if name else "?"


# === Legacy fixture mode ===


def _discover_legacy_mode(repo_root: Path) -> DiscoveredCatalog:
    """Discover ``docs/tasks/block_*/`` without YAML — synthetic fixture.

    Per D16.6: legacy fixture without ``project.yaml`` maps to a single
    implicit project ``fixture``; folder = directory name (``block_*``).
    Task meta comes from H1 + bold lines (handled by :mod:`ego.parser`).
    """
    proj = Project(
        id=FIXTURE_PROJECT_ID,
        name=FIXTURE_PROJECT_NAME,
        description="Legacy docs/tasks/ layout — no catalog.yaml",
        version="1.0.0",
        version_policy="auto_minor",
        path=repo_root,
    )
    dp = DiscoveredProject(project=proj)
    for block_dir in sorted(repo_root.iterdir()):
        if not block_dir.is_dir() or block_dir.name.startswith("."):
            continue
        code = _guess_code_from_dirname(block_dir.name)
        folder = Folder(
            id=block_dir.name,
            code=code,
            name=block_dir.name.replace("_", " ").title(),
            path=block_dir,
            project_id=FIXTURE_PROJECT_ID,
        )
        df = DiscoveredFolder(folder=folder)
        df.tasks = _discover_tasks(block_dir, folder.id, FIXTURE_PROJECT_ID)
        dp.folders.append(df)
    return DiscoveredCatalog(projects=[dp], is_legacy=True)


# === Task discovery (shared by both modes) ===


def _discover_tasks(
    folder_dir: Path, folder_id: str, project_id: str
) -> list[DiscoveredTask]:
    """Find all ``task_*.md`` files in a folder and parse frontmatter."""
    out: list[DiscoveredTask] = []
    for md_path in sorted(folder_dir.glob("task_*.md")):
        fm = _read_frontmatter(md_path)
        solution_path = md_path.with_suffix(".solution.py")
        tests_path = md_path.with_suffix(".tests.py")
        out.append(
            DiscoveredTask(
                md_path=md_path,
                frontmatter=fm,
                solution_path=solution_path if solution_path.is_file() else None,
                tests_path=tests_path if tests_path.is_file() else None,
                folder_id=folder_id,
                project_id=project_id,
            )
        )
    return out


def _read_frontmatter(md_path: Path) -> TaskFrontmatter | None:
    """Read YAML frontmatter from a ``task_*.md`` file. None if absent."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm, _body = parse_task_frontmatter(text)
    return fm
