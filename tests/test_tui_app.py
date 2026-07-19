"""Tests for ego_tui.app — TUI with task editor and check button (textual pilot tests).

Per beads ego-trainer-x4f.1 (skeleton) and x4f.2 (task screen with editor).
Uses textual's Pilot for headless testing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Skip all tests if textual is not installed.
textual = pytest.importorskip("textual")

from ego_tui.app import EgoTUIApp, TaskContent, TaskTree  # noqa: E402
from textual.widgets import Button, TextArea, Tree  # noqa: E402


@pytest.fixture
def docs_dir(tmp_path) -> Path:
    """Create a fake docs/tasks/ with 2 tasks (with tests_code for checking)."""
    docs = tmp_path / "docs" / "tasks"
    f_dir = docs / "block_f_simple"
    f_dir.mkdir(parents=True)
    (f_dir / "task_f1.md").write_text(
        """# Задача F1: Test

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
[(5, 10, "double 5"), (0, 0, "zero")]
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
    (f_dir / "task_f2.md").write_text(
        "# Задача F2: Test2\n\n## Условие\n\nTriple a number.\n",
        encoding="utf-8",
    )
    return docs


@pytest.fixture
def docs_with_student_code(docs_dir):
    """Add student .py files alongside the .md files."""
    (docs_dir / "task_f1.py").write_text(
        "def task_f1_double(n):\n    return n * 2\n",
        encoding="utf-8",
    )
    return docs_dir


@pytest.mark.anyio
async def test_app_launches(docs_dir):
    """App should launch and have the expected widgets."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query("Header")
        assert app.query("Footer")
        tree = app.query_one("#task-tree", TaskTree)
        assert tree is not None
        content = app.query_one("#task-content", TaskContent)
        assert content is not None


@pytest.mark.anyio
async def test_task_tree_populated(docs_dir):
    """Tree should have blocks and tasks from docs/tasks/."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        assert len(tree.root.children) == 1
        block_node = tree.root.children[0]
        assert "F" in block_node.label.plain
        assert len(block_node.children) == 2
        labels = [c.label.plain for c in block_node.children]
        assert "F1" in labels
        assert "F2" in labels


@pytest.mark.anyio
async def test_selecting_task_shows_content(docs_dir):
    """Selecting a task leaf should update the content pane."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        block_node = tree.root.children[0]
        block_node.expand()
        await pilot.pause()
        f1_node = block_node.children[0]
        tree.select_node(f1_node)
        tree.post_message(Tree.NodeSelected(f1_node))
        await pilot.pause()
        content = app.query_one("#task-content", TaskContent)
        assert content is not None
        assert content.current_task_id == "F1"


@pytest.mark.anyio
async def test_empty_docs_dir(tmp_path):
    """App should handle missing docs/tasks/ gracefully."""
    app = EgoTUIApp(docs_dir=tmp_path / "nonexistent")
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        assert len(tree.root.children) >= 1
        first_child = tree.root.children[0]
        assert "not found" in first_child.label.plain.lower()


@pytest.mark.anyio
async def test_quit_binding(docs_dir):
    """Pressing q should quit the app."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("q")
        await pilot.pause()
        assert app._return_value is None or app._return_value == 0


@pytest.mark.anyio
async def test_task_tree_has_blocks_with_multiple_dirs(tmp_path):
    """Tree should group tasks by block directory."""
    docs = tmp_path / "docs" / "tasks"
    (docs / "block_f_simple").mkdir(parents=True)
    (docs / "block_h_more").mkdir(parents=True)
    (docs / "block_f_simple" / "task_f1.md").write_text("# F1", encoding="utf-8")
    (docs / "block_h_more" / "task_h1.md").write_text("# H1", encoding="utf-8")

    app = EgoTUIApp(docs_dir=docs)
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        assert len(tree.root.children) == 2
        block_labels = [c.label.plain for c in tree.root.children]
        assert any("F" in l for l in block_labels)
        assert any("H" in l for l in block_labels)


# === x4f.2: editor + check button (DEFERRED — TUI frozen per ADR-0014) ===

# These tests are skipped because TUI is frozen (ADR-0014).
# VSCode extension is the primary UI now.

pytestmark_x4f2 = pytest.mark.skip(reason="TUI frozen per ADR-0014 — VSCode extension is primary UI")


@pytestmark_x4f2
@pytest.mark.anyio
async def test_editor_widget_present(docs_dir):
    """Code editor (TextArea) should be present in the content pane."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#code-editor", TextArea)
        assert editor is not None


@pytestmark_x4f2
@pytest.mark.anyio
async def test_check_button_present(docs_dir):
    """The 'Проверить' button should be present."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        button = app.query_one("#check-button", Button)
        assert button is not None
        assert "Проверить" in button.label.plain or "Check" in button.label.plain


@pytestmark_x4f2
@pytest.mark.anyio
async def test_selecting_task_loads_code_into_editor(docs_with_student_code):
    """Selecting a task should load student code into the editor."""
    app = EgoTUIApp(docs_dir=docs_with_student_code)
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        block_node = tree.root.children[0]
        block_node.expand()
        await pilot.pause()
        f1_node = block_node.children[0]
        tree.select_node(f1_node)
        tree.post_message(Tree.NodeSelected(f1_node))
        await pilot.pause()
        editor = app.query_one("#code-editor", TextArea)
        assert "task_f1_double" in editor.text
        assert "return n * 2" in editor.text


@pytestmark_x4f2
@pytest.mark.anyio
async def test_check_button_runs_checker(docs_with_student_code):
    """Pressing the check button should run the checker and show results."""
    app = EgoTUIApp(docs_dir=docs_with_student_code)
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        block_node = tree.root.children[0]
        block_node.expand()
        await pilot.pause()
        f1_node = block_node.children[0]
        tree.select_node(f1_node)
        tree.post_message(Tree.NodeSelected(f1_node))
        await pilot.pause()
        button = app.query_one("#check-button", Button)
        button.press()
        await pilot.pause()
        await pilot.pause()
        result = app.query_one("#check-result")
        result_text = str(result.renderable) if hasattr(result, "renderable") else ""
        assert "PASSED" in result_text or "NO_TESTS" in result_text or "Checking" in result_text


@pytestmark_x4f2
@pytest.mark.anyio
async def test_check_keyboard_shortcut(docs_with_student_code):
    """Pressing 'c' should trigger the check action."""
    app = EgoTUIApp(docs_dir=docs_with_student_code)
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        block_node = tree.root.children[0]
        block_node.expand()
        await pilot.pause()
        f1_node = block_node.children[0]
        tree.select_node(f1_node)
        tree.post_message(Tree.NodeSelected(f1_node))
        await pilot.pause()
        await pilot.press("c")
        await pilot.pause()
        await pilot.pause()
        result = app.query_one("#check-result")
        result_text = str(result.renderable) if hasattr(result, "renderable") else ""
        assert "PASSED" in result_text or "NO_TESTS" in result_text or "Checking" in result_text


@pytestmark_x4f2
@pytest.mark.anyio
async def test_editor_editable(docs_dir):
    """Editor should be editable (user can type code)."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#code-editor", TextArea)
        editor.text = "def foo():\n    return 42\n"
        await pilot.pause()
        assert "def foo" in editor.text
        assert "return 42" in editor.text
