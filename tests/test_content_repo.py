"""Tests for ego.content_repo — walker for Project/Folder/Task layout.

Covers both catalog mode (new layout with YAML) and legacy fixture mode
(``docs/tasks/block_*/`` without YAML → synthetic ``fixture`` project).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ego.content_repo import (
    FIXTURE_PROJECT_ID,
    discover_repo,
)


# === Fixtures ===


@pytest.fixture
def new_layout_repo(tmp_path: Path) -> Path:
    """Build a minimal content-repo in new (catalog) layout."""
    root = tmp_path / "ego-tasks"
    root.mkdir()
    (root / "catalog.yaml").write_text(
        "schema_version: 1\n"
        "projects:\n"
        "  - id: junior-core\n"
        "    path: projects/junior-core\n"
        "    enabled: true\n"
        "  - id: llm-track\n"
        "    path: projects/llm-track\n"
        "    enabled: false\n",
        encoding="utf-8",
    )
    proj = root / "projects" / "junior-core"
    (proj / "folders").mkdir(parents=True)
    (proj / "project.yaml").write_text(
        "id: junior-core\n"
        'name: "Junior Core"\n'
        'description: "Base track"\n'
        'version: "1.2.0"\n'
        "order: 10\n",
        encoding="utf-8",
    )

    # Folder block_f_simple with one task (frontmatter + sidecars).
    f = proj / "folders" / "block_f_simple"
    f.mkdir()
    (f / "folder.yaml").write_text(
        "id: block_f_simple\n"
        "code: F\n"
        'name: "Базовые паттерны"\n'
        "level: easy\n",
        encoding="utf-8",
    )
    (f / "task_f1.md").write_text(
        "---\n"
        "id: F1\n"
        'title: "Test F1"\n'
        'version: "1.0.0"\n'
        "level: easy\n"
        "tags: [find]\n"
        "---\n\n"
        "# Задача F1: Test\n\n## Условие\nDo the thing.\n",
        encoding="utf-8",
    )
    (f / "task_f1.solution.py").write_text("def task_f1():\n    return 42\n", encoding="utf-8")
    (f / "task_f1.tests.py").write_text("# tests\n", encoding="utf-8")

    # Folder block_h without folder.yaml (synthetic).
    f2 = proj / "folders" / "block_h_more"
    f2.mkdir()
    (f2 / "task_h1.md").write_text(
        "---\n"
        "id: H1\n"
        'title: "Test H1"\n'
        "---\n\n"
        "# Задача H1: ...\n",
        encoding="utf-8",
    )

    # Disabled project (llm-track) — should be skipped.
    (root / "projects" / "llm-track").mkdir(parents=True)
    return root


@pytest.fixture
def legacy_repo(tmp_path: Path) -> Path:
    """Build a minimal legacy ``docs/tasks/`` layout (no catalog.yaml)."""
    root = tmp_path / "docs" / "tasks"
    root.mkdir(parents=True)
    # block_f_simple with one .md (no frontmatter, no YAML).
    f = root / "block_f_simple"
    f.mkdir()
    (f / "task_f1.md").write_text(
        "# Задача F1: Test\n"
        "**Блок:** F — Patterns\n"
        "**Сложность:** easy\n"
        "**Темы:** find\n\n"
        "## Условие\nDo the thing.\n",
        encoding="utf-8",
    )
    (f / "task_f1.solution.py").write_text("def task_f1():\n    return 42\n", encoding="utf-8")
    # block_1_logs with one .md.
    f2 = root / "block_1_logs"
    f2.mkdir()
    (f2 / "task_1_1.md").write_text(
        "# Задача 1.1: Logs\n"
        "**Блок:** 1 — Logs\n"
        "**Сложность:** medium\n"
        "**Темы:** logs\n\n"
        "## Условие\nParse logs.\n",
        encoding="utf-8",
    )
    return root


# === Catalog mode (new layout) ===


def test_discover_catalog_mode_basic(new_layout_repo: Path):
    cat = discover_repo(new_layout_repo)
    assert cat.is_legacy is False
    assert len(cat.projects) == 1  # llm-track disabled → skipped
    proj = cat.projects[0]
    assert proj.project.id == "junior-core"
    assert proj.project.name == "Junior Core"
    assert proj.project.version == "1.2.0"
    assert proj.project.path == (new_layout_repo / "projects" / "junior-core").resolve()


def test_discover_catalog_mode_disabled_project_skipped(new_layout_repo: Path):
    cat = discover_repo(new_layout_repo)
    ids = [p.project.id for p in cat.projects]
    assert "llm-track" not in ids


def test_discover_catalog_mode_folders(new_layout_repo: Path):
    cat = discover_repo(new_layout_repo)
    proj = cat.projects[0]
    folder_ids = [f.folder.id for f in proj.folders]
    assert "block_f_simple" in folder_ids
    assert "block_h_more" in folder_ids


def test_discover_catalog_mode_folder_with_yaml(new_layout_repo: Path):
    cat = discover_repo(new_layout_repo)
    proj = cat.projects[0]
    f = next(f for f in proj.folders if f.folder.id == "block_f_simple")
    assert f.folder.code == "F"
    assert f.folder.name == "Базовые паттерны"
    assert f.folder.level == "easy"
    assert f.folder.project_id == "junior-core"


def test_discover_catalog_mode_folder_synthetic(new_layout_repo: Path):
    """Folder without folder.yaml → synthetic from dir name."""
    cat = discover_repo(new_layout_repo)
    proj = cat.projects[0]
    f = next(f for f in proj.folders if f.folder.id == "block_h_more")
    assert f.folder.code == "H"  # guessed from block_h_more
    assert f.folder.project_id == "junior-core"


def test_discover_catalog_mode_task_frontmatter(new_layout_repo: Path):
    cat = discover_repo(new_layout_repo)
    proj = cat.projects[0]
    f = next(f for f in proj.folders if f.folder.id == "block_f_simple")
    t = f.tasks[0]
    assert t.frontmatter is not None
    assert t.frontmatter.id == "F1"
    assert t.frontmatter.title == "Test F1"
    assert t.frontmatter.version == "1.0.0"
    assert t.solution_path is not None
    assert t.solution_path.name == "task_f1.solution.py"
    assert t.tests_path is not None
    assert t.folder_id == "block_f_simple"
    assert t.project_id == "junior-core"


def test_discover_catalog_mode_all_tasks_flattens(new_layout_repo: Path):
    cat = discover_repo(new_layout_repo)
    all_tasks = cat.all_tasks
    assert len(all_tasks) == 2  # task_f1 + task_h1
    ids = {t.frontmatter.id if t.frontmatter else None for t in all_tasks}
    assert ids == {"F1", "H1"}


# === Legacy fixture mode ===


def test_discover_legacy_mode_basic(legacy_repo: Path):
    cat = discover_repo(legacy_repo)
    assert cat.is_legacy is True
    assert len(cat.projects) == 1
    proj = cat.projects[0]
    assert proj.project.id == FIXTURE_PROJECT_ID
    assert proj.project.version_policy == "auto_minor"


def test_discover_legacy_mode_folders_from_dirnames(legacy_repo: Path):
    cat = discover_repo(legacy_repo)
    proj = cat.projects[0]
    folder_ids = [f.folder.id for f in proj.folders]
    assert "block_f_simple" in folder_ids
    assert "block_1_logs" in folder_ids


def test_discover_legacy_mode_folder_code_guessed(legacy_repo: Path):
    cat = discover_repo(legacy_repo)
    proj = cat.projects[0]
    f1 = next(f for f in proj.folders if f.folder.id == "block_f_simple")
    assert f1.folder.code == "F"
    f2 = next(f for f in proj.folders if f.folder.id == "block_1_logs")
    assert f2.folder.code == "1"


def test_discover_legacy_mode_task_no_frontmatter(legacy_repo: Path):
    """Legacy .md without frontmatter → frontmatter is None (parser handles)."""
    cat = discover_repo(legacy_repo)
    proj = cat.projects[0]
    f = next(f for f in proj.folders if f.folder.id == "block_f_simple")
    t = f.tasks[0]
    assert t.frontmatter is None
    assert t.solution_path is not None
    assert t.tests_path is None  # no .tests.py in this fixture
    assert t.project_id == FIXTURE_PROJECT_ID


def test_discover_legacy_mode_all_tasks(legacy_repo: Path):
    cat = discover_repo(legacy_repo)
    assert len(cat.all_tasks) == 2


# === Edge cases ===


def test_discover_repo_missing_dir_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        discover_repo(tmp_path / "does-not-exist")


def test_discover_repo_empty_dir_is_legacy(tmp_path: Path):
    """Empty dir → legacy mode with no folders (synthetic fixture)."""
    cat = discover_repo(tmp_path)
    assert cat.is_legacy is True
    assert len(cat.projects) == 1
    assert cat.projects[0].folders == []


def test_discover_real_docs_tasks_fixture():
    """Smoke test: discover the real docs/tasks/ in this repo.

    Must be legacy mode with 8 blocks (block_f_simple, block_h_more_domains,
    block_1_logs, block_a_join, block_b_sanitize, block_c_flatten,
    block_d_variety, block_g_nlp).
    """
    repo_root = Path(__file__).parent.parent / "docs" / "tasks"
    if not repo_root.is_dir():
        pytest.skip("docs/tasks/ not available")
    cat = discover_repo(repo_root)
    assert cat.is_legacy is True
    assert len(cat.projects) == 1
    proj = cat.projects[0]
    assert proj.project.id == FIXTURE_PROJECT_ID
    # All 8 blocks should be discovered.
    folder_ids = {f.folder.id for f in proj.folders}
    expected = {
        "block_f_simple",
        "block_h_more_domains",
        "block_1_logs",
        "block_a_join",
        "block_b_sanitize",
        "block_c_flatten",
        "block_d_variety",
        "block_g_nlp",
    }
    assert expected.issubset(folder_ids)
    # All tasks should have None frontmatter (legacy .md without YAML).
    for t in cat.all_tasks:
        assert t.frontmatter is None
