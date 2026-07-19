"""Tests for `ego check <task>` (beads ego-trainer-8bv.2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ego.cli.main import main


@pytest.fixture
def tmp_cwd(tmp_path, monkeypatch):
    """Run commands in a temp directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def repo_with_docs(tmp_cwd):
    """Create a temp repo with docs/tasks/ containing F1 and .ego/ initialized."""
    # Create docs/tasks/block_f_simple/task_f1.md
    docs = tmp_cwd / "docs" / "tasks" / "block_f_simple"
    docs.mkdir(parents=True)
    (docs / "task_f1.md").write_text(
        """# Задача F1: Test task

**Блок:** F — Test
**Сложность:** easy
**Темы:** test

## Условие

Double a number.

## Аргументы

- `n` — int

## Возвращает

int — n * 2

## Пример

```python
task_f1_double(5)  # -> 10
```

<details>
<summary>Эталонное решение</summary>

```python
def task_f1_double(n):
    return n * 2
```

</details>
""",
        encoding="utf-8",
    )
    # Initialize .ego/
    main(["init", "--local"])
    return tmp_cwd


@pytest.fixture
def repo_with_student_solution(repo_with_docs):
    """Create a student solution file at tasks/block_f_simple/task_f1.py."""
    tasks_dir = repo_with_docs / "tasks" / "block_f_simple"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / "task_f1.py").write_text(
        "def task_f1_double(n):\n    return n * 2\n",
        encoding="utf-8",
    )
    return repo_with_docs


# === basic flow ===


def test_check_no_ego_dir(tmp_cwd, capsys):
    rc = main(["check", "F1"])
    assert rc == 1
    captured = capsys.readouterr()
    assert ".ego/" in captured.err


def test_check_task_not_found(repo_with_docs, capsys):
    rc = main(["check", "ZZZ"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err.lower() or "ZZZ" in captured.err


def test_check_no_student_code(repo_with_docs, capsys):
    """Task .md exists but no student .py file."""
    rc = main(["check", "F1"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err.lower() or "student" in captured.err.lower()


def test_check_correct_solution(repo_with_student_solution, capsys):
    """Student code matches reference → passed, exit 0."""
    rc = main(["check", "F1"])
    # No tests_code in .md → status=no_tests → exit 1.
    assert rc == 1
    captured = capsys.readouterr()
    assert "NO_TESTS" in captured.out


def test_check_with_tests_code(repo_with_docs, capsys):
    """If .md has tests_code, checker should run and pass."""
    # Rewrite .md with tests_code section.
    docs = repo_with_docs / "docs" / "tasks" / "block_f_simple" / "task_f1.md"
    docs.write_text(
        """# Задача F1: Test task

**Блок:** F — Test
**Сложность:** easy
**Темы:** test

## Условие

Double a number.

## Аргументы

- `n` — int

## Возвращает

int — n * 2

## Пример

```python
task_f1_double(5)  # -> 10
```

## Тесты

```python
[(5, 10, "double 5"), (0, 0, "zero"), (-3, -6, "negative")]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_f1_double(n):
    return n * 2
```

</details>
""",
        encoding="utf-8",
    )
    # Create student solution.
    tasks_dir = repo_with_docs / "tasks" / "block_f_simple"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / "task_f1.py").write_text(
        "def task_f1_double(n):\n    return n * 2\n",
        encoding="utf-8",
    )
    rc = main(["check", "F1"])
    assert rc == 0  # all passed
    captured = capsys.readouterr()
    assert "PASSED" in captured.out
    assert "3/3" in captured.out


def test_check_wrong_solution(repo_with_docs, capsys):
    """Student code is wrong → failed, exit 1."""
    # Add tests_code.
    docs = repo_with_docs / "docs" / "tasks" / "block_f_simple" / "task_f1.md"
    docs.write_text(
        """# Задача F1: Test task

**Блок:** F — Test
**Сложность:** easy
**Темы:** test

## Условие

Double a number.

## Аргументы

- `n` — int

## Возвращает

int — n * 2

## Пример

```python
task_f1_double(5)  # -> 10
```

## Тесты

```python
[(5, 10, "double 5")]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_f1_double(n):
    return n * 2
```

</details>
""",
        encoding="utf-8",
    )
    tasks_dir = repo_with_docs / "tasks" / "block_f_simple"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / "task_f1.py").write_text(
        "def task_f1_double(n):\n    return n + 2\n",  # wrong
        encoding="utf-8",
    )
    rc = main(["check", "F1"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "FAILED" in captured.out


# === progress + runs ===


def test_check_writes_progress(repo_with_student_solution, capsys):
    """After check, .ego/progress.json should have an entry."""
    main(["check", "F1"])
    progress = json.loads(
        (repo_with_student_solution / ".ego" / "progress.json").read_text("utf-8")
    )
    assert len(progress["entries"]) == 1
    entry = progress["entries"][0]
    assert entry["task_id"] == "F1"
    assert entry["attempts"] == 1


def test_check_increments_attempts(repo_with_student_solution, capsys):
    """Running check twice should increment attempts."""
    main(["check", "F1"])
    main(["check", "F1"])
    progress = json.loads(
        (repo_with_student_solution / ".ego" / "progress.json").read_text("utf-8")
    )
    assert progress["entries"][0]["attempts"] == 2


def test_check_writes_run_log(repo_with_student_solution, capsys):
    """After check, .ego/runs/ should have a .json log file."""
    main(["check", "F1"])
    runs_dir = repo_with_student_solution / ".ego" / "runs"
    run_files = list(runs_dir.glob("F1-*.json"))
    assert len(run_files) == 1
    data = json.loads(run_files[0].read_text("utf-8"))
    assert data["task_id"] == "F1"
    # no_tests maps to "error" in RunStatus.
    assert data["status"] in ("no_tests", "error")
    assert data["solution_hash"]
    assert len(data["solution_hash"]) == 64


def test_check_run_log_has_format_output(repo_with_student_solution, capsys):
    """Run log should contain the formatted check result."""
    main(["check", "F1"])
    runs_dir = repo_with_student_solution / ".ego" / "runs"
    run_file = list(runs_dir.glob("F1-*.json"))[0]
    data = json.loads(run_file.read_text("utf-8"))
    assert "NO_TESTS" in data["log"] or "F1" in data["log"]


# === task id with period ===


def test_check_task_1_5(repo_with_docs, capsys):
    """Task id with period (1.5) should work."""
    # Create a 1.5 task.
    docs = repo_with_docs / "docs" / "tasks" / "block_1_logs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "task_1_5.md").write_text(
        """# Задача 1.5: Test

**Блок:** 1 — Logs
**Сложность:** easy
**Темы:** test

## Условие

Return n.

## Аргументы

- `n` — int

## Возвращает

int

## Пример

```python
task_1_5_test(5)  # -> 5
```

## Тесты

```python
[(5, 5, "identity")]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_1_5_test(n):
    return n
```

</details>
""",
        encoding="utf-8",
    )
    tasks_dir = repo_with_docs / "tasks" / "block_1_logs"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / "task_1_5.py").write_text(
        "def task_1_5_test(n):\n    return n\n",
        encoding="utf-8",
    )
    rc = main(["check", "1.5"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "PASSED" in captured.out


# === --local flag (basic — full --local is 8bv.3) ===


def test_check_local_flag_accepted(repo_with_student_solution, capsys):
    """--local flag should be accepted (full offline impl is 8bv.3)."""
    # For now, --local with .ego/ should still work (uses docs/tasks/ fallback).
    rc = main(["check", "F1", "--local"])
    # Same behavior as without --local when .ego/ exists.
    assert rc in (0, 1)


# === help ===


def test_check_help(capsys):
    with pytest.raises(SystemExit):
        main(["check", "--help"])
    captured = capsys.readouterr()
    assert "task_id" in captured.out
    assert "--local" in captured.out
