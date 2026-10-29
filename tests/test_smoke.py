"""Smoke tests — package imports, CLI runs."""

import importlib


def test_import_ego():
    import ego
    assert ego.__version__


def test_import_submodules():
    for name in ("ego.parser", "ego.runner", "ego.checker", "ego.models", "ego.progress"):
        assert importlib.import_module(name)


def test_cli_version(capsys):
    from ego.cli.main import main
    try:
        main(["--version"])
    except SystemExit as e:
        assert e.code == 0
    captured = capsys.readouterr()
    assert "ego" in captured.out


def test_33_task_files_exist(tasks_dir):
    files = list(tasks_dir.rglob("*.md"))
    assert len(files) == 33, f"Expected 33 task .md files, got {len(files)}"
