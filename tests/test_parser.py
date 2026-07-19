"""Tests for ego.parser — parsing 33 existing .md files + edge cases."""

from pathlib import Path

import pytest

from ego.models import Task
from ego.parser import (
    _generate_stub,
    _hash_content,
    parse_task_file,
    parse_task_text,
)


# === Helpers ===


def _find_task(tasks_dir: Path, name: str) -> Path:
    """Find a task file by name like 'task_f1.md'."""
    for p in tasks_dir.rglob("*.md"):
        if p.name == name:
            return p
    raise FileNotFoundError(name)


# === Smoke: parse all 33 ===


def test_parse_all_33_tasks(task_files):
    """Every .md in docs/tasks/ should parse successfully."""
    for path in task_files:
        task = parse_task_file(path)
        assert isinstance(task, Task)
        assert task.id, f"empty id in {path}"
        assert task.block, f"empty block in {path}"
        assert task.title, f"empty title in {path}"
        assert task.level in ("easy", "medium", "hard"), f"bad level in {path}: {task.level}"
        assert task.statement_md, f"empty statement in {path}"
        assert task.solution_py, f"empty solution in {path}"
        assert task.stub_py, f"empty stub in {path}"
        assert task.content_hash, f"empty hash in {path}"
        assert len(task.content_hash) == 64, f"hash not sha256 in {path}"


def test_parse_all_33_count(task_files):
    """Should be 33 parseable tasks."""
    assert len(task_files) == 33


# === Specific tasks ===


def test_parse_f1(tasks_dir):
    path = _find_task(tasks_dir, "task_f1.md")
    task = parse_task_file(path)
    assert task.id == "F1"
    assert task.block == "F"
    assert task.slug == "block_f_simple"
    assert task.task_id == "F1"
    assert task.title == "Найди первый критический баг"
    assert task.level == "easy"
    assert "find" in task.tags or "filter" in task.tags  # tags могут отличаться
    # solution должен содержать функцию task_f1_find_critical
    assert "def task_f1_find_critical" in task.solution_py
    # stub должен содержать сигнатуру и pass
    assert "def task_f1_find_critical" in task.stub_py
    assert "pass" in task.stub_py
    # stub НЕ должен содержать реализацию
    assert 'return b["title"]' not in task.stub_py


def test_parse_1_5(tasks_dir):
    path = _find_task(tasks_dir, "task_1_5.md")
    task = parse_task_file(path)
    assert task.id == "1.5"
    assert task.block == "1"
    assert task.slug == "block_1_logs"
    assert task.level == "medium"
    assert "def task_1_5_sla_report" in task.solution_py
    assert "def task_1_5_sla_report" in task.stub_py


def test_parse_b_sanitize_keeps_helper(tasks_dir):
    """Block B has _is_email helper in solution — parser must keep it."""
    path = _find_task(tasks_dir, "task_b.md")
    task = parse_task_file(path)
    assert "def _is_email" in task.solution_py
    assert "def task_b_sanitize" in task.solution_py
    # stub должен содержать ТОЛЬКО task_b_sanitize (без _is_email)
    assert "def task_b_sanitize" in task.stub_py
    assert "def _is_email" not in task.stub_py, "stub should NOT include helper"


def test_parse_h8(tasks_dir):
    path = _find_task(tasks_dir, "task_h8.md")
    task = parse_task_file(path)
    assert task.id == "H8"
    assert task.block == "H"
    assert task.level == "medium"
    assert "def task_h8_tiered_synthesis" in task.solution_py


def test_parse_a_join(tasks_dir):
    path = _find_task(tasks_dir, "task_a.md")
    task = parse_task_file(path)
    assert task.id == "A"
    assert task.block == "A"
    assert task.level == "hard"
    assert "def task_a_merge_runs" in task.solution_py


# === Statement_md ===


def test_statement_excludes_solution_and_tests(tasks_dir):
    path = _find_task(tasks_dir, "task_f1.md")
    task = parse_task_file(path)
    # statement не должен содержать код эталона
    assert "def task_f1_find_critical" not in task.statement_md
    # но должен содержать Пример
    assert "Пример" in task.statement_md or "```python" in task.statement_md


def test_statement_includes_uslovia(tasks_dir):
    path = _find_task(tasks_dir, "task_1_5.md")
    task = parse_task_file(path)
    assert "## Условие" in task.statement_md
    assert "## Аргументы" in task.statement_md
    assert "## Правила" in task.statement_md


# === Stub generation ===


def test_stub_has_pass(tasks_dir):
    path = _find_task(tasks_dir, "task_f2.md")
    task = parse_task_file(path)
    assert "pass" in task.stub_py


def test_stub_preserves_signature(tasks_dir):
    path = _find_task(tasks_dir, "task_h2.md")
    task = parse_task_file(path)
    # h2 имеет def task_h2_loot_drop(drops, seed=42)
    assert "def task_h2_loot_drop(drops, seed=42)" in task.stub_py


def test_stub_excludes_solution_body(tasks_dir):
    path = _find_task(tasks_dir, "task_d1.md")
    task = parse_task_file(path)
    # в эталоне есть result.get(cat, 0) — в stub этого быть не должно
    assert "result.get(cat, 0)" not in task.stub_py


# === Content hash ===


def test_content_hash_stable(tasks_dir):
    """Same file → same hash."""
    path = _find_task(tasks_dir, "task_f1.md")
    t1 = parse_task_file(path)
    t2 = parse_task_file(path)
    assert t1.content_hash == t2.content_hash


def test_content_hash_differs_across_tasks(tasks_dir):
    paths = [_find_task(tasks_dir, n) for n in ("task_f1.md", "task_f2.md", "task_f3.md")]
    hashes = [parse_task_file(p).content_hash for p in paths]
    assert len(set(hashes)) == 3


# === Error cases ===


def test_missing_uslovie_raises():
    bad = (
        "# Задача X: Test\n\n"
        "**Блок:** X — Test\n"
        "**Сложность:** easy\n"
        "**Темы:** x\n\n"
        "## Аргументы\n\n- a\n"
    )
    with pytest.raises(ValueError, match="Условие"):
        parse_task_text(bad, path=Path("test.md"))


def test_missing_solution_raises():
    bad = """# Задача X: Test

**Блок:** X — Test
**Сложность:** easy
**Темы:** x

## Условие

Test condition.

## Аргументы

- a

## Возвращает

int
"""
    with pytest.raises(ValueError, match="Эталон"):
        parse_task_text(bad, path=Path("test.md"))


def test_invalid_title_raises():
    bad = "# Not a task\n"
    with pytest.raises(ValueError, match="title"):
        parse_task_text(bad, path=Path("test.md"))


def test_missing_block_meta_raises():
    bad = """# Задача X: Test

**Сложность:** easy
**Темы:** x

## Условие

x

## Аргументы

- a
"""
    with pytest.raises(ValueError, match="Блок"):
        parse_task_text(bad, path=Path("test.md"))


# === Future: ## Тесты section ===


def test_parse_tests_section_when_present():
    """When ## Тесты section exists, parser should extract its Python code."""
    md = """# Задача Z: Test

**Блок:** Z — Test
**Сложность:** easy
**Темы:** x

## Условие

Test.

## Аргументы

- a

## Возвращает

int

## Правила

- правило

## Пример

```python
>>> z(1)
2
```

## Тесты

```python
[
    (1, 2, "happy"),
    (0, 1, "zero"),
]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_z(a):
    return a + 1
```

</details>
"""
    task = parse_task_text(md, path=Path("block_z/test_z.md"))
    assert "tests_code" in task.extra
    tests_code = task.extra["tests_code"]
    assert "(1, 2" in tests_code
    assert "(0, 1" in tests_code


def test_tests_section_absent_means_no_tests_code(tasks_dir):
    path = _find_task(tasks_dir, "task_f1.md")
    task = parse_task_file(path)
    # Существующие 33 файла НЕ имеют ## Тесты
    assert "tests_code" not in task.extra or not task.extra["tests_code"]
