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

import re
from dataclasses import dataclass, field
from pathlib import Path

from ego.catalog import (
    Catalog,
    Folder,
    LessonFrontmatter,
    Project,
    TaskFrontmatter,
    load_catalog,
    load_folder_file,
    load_project_file,
    parse_lesson_frontmatter,
    parse_task_frontmatter,
)
from ego.runner import include_matches

# === Discovered structures ===

FIXTURE_PROJECT_ID = "fixture"
FIXTURE_PROJECT_NAME = "Fixture (legacy docs/tasks)"

#: Project directories inside a ``kind: challenge`` folder (ADR-0018 D18.1).
STARTER_DIR = "starter"
SOLUTION_DIR = "solution"

# ``stage_01_parse.md`` → number 1, slug ``parse``.
_STAGE_MD_RE = re.compile(r"^stage_(?P<number>\d{2})_(?P<slug>[^/]+)\.md$")


@dataclass
class DiscoveredTask:
    """One task file on disk + parsed frontmatter (if any).

    For a challenge stage, ``stage`` is its 1-based number and
    ``stage_solution`` the optional ``stage_NN_<slug>.solution/`` project
    (the reference right after that stage); the code itself lives in the
    folder's ``starter/`` / ``solution/`` directories (ADR-0018 D18.1).
    """

    md_path: Path
    frontmatter: TaskFrontmatter | None  # None = legacy, fall back to parser
    solution_path: Path | None  # <slug>.solution.py next to .md
    tests_path: Path | None  # <slug>.tests.py next to .md
    folder_id: str  # parent folder id (slug)
    project_id: str  # parent project id
    stage: int | None = None  # 1-based stage number of a challenge
    stage_solution: Path | None = None


@dataclass
class DiscoveredLesson:
    """One ``lesson_*.md`` theory card on disk (catalog mode only).

    ``frontmatter`` is ``None`` when the file could not be parsed — the
    ``error`` string then explains why (reported by sync, never fatal).
    """

    md_path: Path
    frontmatter: LessonFrontmatter | None = None
    body_md: str = ""
    error: str = ""
    folder_id: str = ""  # parent folder id (slug)
    project_id: str = ""  # parent project id


@dataclass
class DiscoveredFolder:
    """One folder (block) with its meta and discovered tasks + lessons.

    ``starter`` / ``solution`` are the project directories of a challenge
    folder (``None`` when absent, and for an ordinary folder).
    """

    folder: Folder
    tasks: list[DiscoveredTask] = field(default_factory=list)
    lessons: list[DiscoveredLesson] = field(default_factory=list)
    starter: Path | None = None
    solution: Path | None = None

    @property
    def is_challenge(self) -> bool:
        """True when the folder declares ``kind: challenge``."""
        return self.folder.kind == "challenge"


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

    @property
    def all_lessons(self) -> list[DiscoveredLesson]:
        """Flatten all discovered lessons across projects/folders."""
        return [lesson for p in self.projects for f in p.folders for lesson in f.lessons]

    @property
    def challenge_folders(self) -> list[DiscoveredFolder]:
        """Folders with ``kind: challenge`` (ADR-0018), in catalog order."""
        return [f for p in self.projects for f in p.folders if f.is_challenge]


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
        if folder.is_challenge:
            df.starter = _dir_or_none(folder_dir / STARTER_DIR)
            df.solution = _dir_or_none(folder_dir / SOLUTION_DIR)
        df.tasks = _discover_tasks(
            folder_dir, folder.id, project_id, is_challenge=folder.is_challenge
        )
        df.lessons = _discover_lessons(folder_dir, folder.id, project_id)
        out.append(df)
    return out


def _dir_or_none(path: Path) -> Path | None:
    """``path`` when it is a directory, else ``None``."""
    return path if path.is_dir() else None


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
        # Legacy layout has no lessons; a stray lesson_*.md is ignored.
        dp.folders.append(df)
    return DiscoveredCatalog(projects=[dp], is_legacy=True)


# === Task discovery (shared by both modes) ===


def _discover_tasks(
    folder_dir: Path,
    folder_id: str,
    project_id: str,
    *,
    is_challenge: bool = False,
) -> list[DiscoveredTask]:
    """Find the folder's tasks and parse their frontmatter.

    A challenge folder yields its ``stage_NN_<slug>.md`` stages instead of
    ``task_*.md`` files; the stage file's slug becomes the task slug, so its
    tests live in ``stage_NN_<slug>.tests.py`` and its optional reference
    project in ``stage_NN_<slug>.solution/``. ``stage_NN_<slug>.solution/``
    is a directory, so it never shows up in the glob patterns.
    """
    if is_challenge:
        out = []
        stages = _stage_files(folder_dir)
        numbers = [number for number, _ in stages]
        if numbers and numbers != list(range(1, len(numbers) + 1)):
            raise ValueError(
                f"{folder_dir.name}: этапы челленджа должны идти подряд с 1 "
                f"(stage_01_…, stage_02_…), найдено: {numbers}"
            )
        for number, md_path in stages:
            slug = f"stage_{number:02}_{_stage_slug(md_path)}"
            tests_path = folder_dir / f"{slug}.tests.py"
            out.append(
                DiscoveredTask(
                    md_path=md_path,
                    frontmatter=_read_frontmatter(md_path),
                    solution_path=None,  # code lives in the folder (D18.1)
                    tests_path=tests_path if tests_path.is_file() else None,
                    folder_id=folder_id,
                    project_id=project_id,
                    stage=number,
                    stage_solution=_dir_or_none(folder_dir / f"{slug}.solution"),
                )
            )
        return out

    out = []
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


def _stage_files(folder_dir: Path) -> list[tuple[int, Path]]:
    """``(number, path)`` of every ``stage_NN_<slug>.md`` in a challenge."""
    stages = []
    for md_path in sorted(folder_dir.glob("stage_*.md")):
        match = _STAGE_MD_RE.match(md_path.name)
        if match is None:
            raise ValueError(
                f"{md_path.name}: имя этапа должно быть stage_NN_<slug>.md "
                "(NN — двузначный номер этапа)"
            )
        stages.append((int(match.group("number")), md_path))
    return stages


def _stage_slug(md_path: Path) -> str:
    """Slug part of ``stage_NN_<slug>.md`` (``"parse"``)."""
    return md_path.stem.split("_", 2)[2]


def _discover_lessons(
    folder_dir: Path, folder_id: str, project_id: str
) -> list[DiscoveredLesson]:
    """Find all ``lesson_*.md`` theory cards in a folder and parse them.

    Parse errors are captured per file (``DiscoveredLesson.error``) so the
    walker never aborts on one bad card; sync reports them as warnings.
    """
    out: list[DiscoveredLesson] = []
    for md_path in sorted(folder_dir.glob("lesson_*.md")):
        lesson = DiscoveredLesson(
            md_path=md_path, folder_id=folder_id, project_id=project_id
        )
        try:
            fm, body = parse_lesson_frontmatter(md_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            lesson.error = str(e)
        else:
            lesson.frontmatter = fm
            lesson.body_md = body
        out.append(lesson)
    return out


def read_project_files(directory: Path, include: list[str] | None = None) -> dict[str, str]:
    """Read a project directory into ``{posix path: text}`` (D18.1).

    Only regular files matching ``include`` (``*.py`` matches every
    directory) are read; hidden directories such as ``.git`` are skipped.
    Text is decoded as UTF-8 with ``surrogateescape`` so binary files
    round-trip unchanged.
    """
    include = list(include or ["*.py"])
    out: dict[str, str] = {}
    for path in sorted(Path(directory).rglob("*")):
        relative = path.relative_to(directory)
        if any(part.startswith(".") for part in relative.parts) or not path.is_file():
            continue
        posix = relative.as_posix()
        if not include_matches(posix, include):
            continue
        out[posix] = path.read_bytes().decode("utf-8", errors="surrogateescape")
    return out


def _read_frontmatter(md_path: Path) -> TaskFrontmatter | None:
    """Read YAML frontmatter from a ``task_*.md`` file. None if absent."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm, _body = parse_task_frontmatter(text)
    return fm
