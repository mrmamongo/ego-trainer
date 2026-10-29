"""Challenge catalog: ``kind: challenge`` folders and ``stage_NN_*.md`` (ADR-0018).

The walker discovers stages as tasks (with their stage number), the folder's
``starter/`` / ``solution/`` projects and the optional per-stage reference
``stage_NN_<slug>.solution/``; :func:`ego.parser.parse_task_file` parses a
stage without requiring a ``.solution.py`` sidecar.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ego.catalog import parse_folder
from ego.content_repo import discover_repo, read_project_files
from ego.parser import is_stage_file, parse_task_file

FIXTURE_CATALOG = Path(__file__).parent / "fixtures" / "challenges_catalog"


def _folder(catalog):
    (folder,) = catalog.challenge_folders
    return folder


def test_challenge_uses_default_workspace():
    folder = parse_folder("id: c\ncode: C\nname: C\n")
    assert folder.kind == "tasks"
    assert folder.workspace is None
    assert not folder.is_challenge


def test_challenge_folder_yaml_is_parsed():
    folder = parse_folder(
        "id: kv_store\ncode: KV\nname: KV Store\nkind: challenge\n"
        "workspace:\n  entry: run.py\n  include: ['*.py']\n  max_files: 5\n"
        "  max_bytes: 1000\n"
    )
    assert folder.is_challenge
    assert folder.workspace is not None
    assert folder.workspace.entry == "run.py"
    assert folder.workspace.max_files == 5


def test_walker_finds_stages_and_projects():
    catalog = discover_repo(FIXTURE_CATALOG)
    folder = _folder(catalog)
    assert folder.folder.kind == "challenge"
    assert [task.stage for task in folder.tasks] == [1, 2]
    assert [task.md_path.name for task in folder.tasks] == [
        "stage_01_parse.md",
        "stage_02_save.md",
    ]
    assert folder.starter is not None and (folder.starter / "main.py").is_file()
    assert folder.solution is not None and (folder.solution / "main.py").is_file()
    # Only stage 2 has its own reference project; stage 1's code is inside it.
    assert folder.tasks[0].stage_solution is None
    assert folder.tasks[1].stage_solution is not None
    assert folder.tasks[0].tests_path is not None
    assert folder.tasks[0].solution_path is None


def test_stage_files_parse_without_solution_sidecar():
    catalog = discover_repo(FIXTURE_CATALOG)
    folder = _folder(catalog)
    stage = parse_task_file(folder.tasks[0].md_path)
    assert stage.id == "KV01"
    assert stage.title == "Разбор команды"
    assert stage.level == "easy"
    assert "parse_command" in stage.statement_md
    assert stage.solution_py == ""
    assert stage.stub_py == ""
    assert stage.tests_file is not None


def test_stage_reference_project_is_the_core_with_files():
    catalog = discover_repo(FIXTURE_CATALOG)
    folder = _folder(catalog)
    stage = parse_task_file(folder.tasks[1].md_path)
    assert stage.extra["solution_source"] == "challenge"
    assert "# === main.py ===" in stage.solution_py
    assert "# === commands.py ===" in stage.solution_py


def test_stage_file_detection():
    assert is_stage_file(Path("stage_01_parse.md"))
    assert not is_stage_file(Path("task_f1.md"))
    assert not is_stage_file(Path("stage_01_parse.tests.py"))


def test_read_project_files_honours_include():
    catalog = discover_repo(FIXTURE_CATALOG)
    folder = _folder(catalog)
    only_py = read_project_files(folder.solution)
    assert sorted(only_py) == ["commands.py", "main.py"]
    with_data = read_project_files(folder.solution, ["*.py", "data/*.json"])
    assert sorted(with_data) == ["commands.py", "main.py"]


def test_stages_must_be_numbered_from_one(tmp_path):
    root = tmp_path / "repo"
    folder_dir = root / "projects" / "p" / "folders" / "c"
    folder_dir.mkdir(parents=True)
    (root / "catalog.yaml").write_text(
        "schema_version: 1\nprojects:\n  - id: p\n    path: projects/p\n", encoding="utf-8"
    )
    (root / "projects" / "p" / "project.yaml").write_text("id: p\nname: P\n", encoding="utf-8")
    (folder_dir / "folder.yaml").write_text(
        "id: c\ncode: C\nname: C\nkind: challenge\n", encoding="utf-8"
    )
    (folder_dir / "stage_02_late.md").write_text("# Задача X: Late\n\n## Условие\nx\n",
                                                 encoding="utf-8")
    with pytest.raises(ValueError, match="stage_01"):
        discover_repo(root)


def test_stage_file_name_must_have_two_digit_number(tmp_path):
    root = tmp_path / "repo"
    folder_dir = root / "projects" / "p" / "folders" / "c"
    folder_dir.mkdir(parents=True)
    (root / "catalog.yaml").write_text(
        "schema_version: 1\nprojects:\n  - id: p\n    path: projects/p\n", encoding="utf-8"
    )
    (root / "projects" / "p" / "project.yaml").write_text("id: p\nname: P\n", encoding="utf-8")
    (folder_dir / "folder.yaml").write_text(
        "id: c\ncode: C\nname: C\nkind: challenge\n", encoding="utf-8"
    )
    (folder_dir / "stage_1_bad.md").write_text("# Задача X: Bad\n\n## Условие\nx\n",
                                               encoding="utf-8")
    with pytest.raises(ValueError, match="stage_NN_"):
        discover_repo(root)
