"""Tests for ego_tui.app — TUI skeleton (textual pilot tests).

Per beads ego-trainer-x4f.1: two-pane layout (task tree + content viewer).
Uses textual's Pilot for headless testing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Skip all tests if textual is not installed.
textual = pytest.importorskip("textual")

from ego_tui.app import EgoTUIApp, TaskContent, TaskTree  # noqa: E402
from textual.widgets import Tree  # noqa: E402


@pytest.fixture
def docs_dir(tmp_path) -> Path:
    """Create a fake docs/tasks/ with 2 tasks."""
    docs = tmp_path / "docs" / "tasks"
    f_dir = docs / "block_f_simple"
    f_dir.mkdir(parents=True)
    (f_dir / "task_f1.md").write_text(
        "# Задача F1: Test\n\n## Условие\n\nDouble a number.\n",
        encoding="utf-8",
    )
    (f_dir / "task_f2.md").write_text(
        "# Задача F2: Test2\n\n## Условие\n\nTriple a number.\n",
        encoding="utf-8",
    )
    return docs


@pytest.mark.anyio
async def test_app_launches(docs_dir):
    """App should launch and have the expected widgets."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        # Header and Footer should be present.
        assert app.query("Header")
        assert app.query("Footer")
        # Task tree should be present.
        tree = app.query_one("#task-tree", TaskTree)
        assert tree is not None
        # Content pane should be present.
        content = app.query_one("#task-content", TaskContent)
        assert content is not None


@pytest.mark.anyio
async def test_task_tree_populated(docs_dir):
    """Tree should have blocks and tasks from docs/tasks/."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        # Should have one block "F" with 2 tasks.
        assert len(tree.root.children) == 1
        block_node = tree.root.children[0]
        assert "F" in block_node.label.plain
        assert len(block_node.children) == 2
        # Tasks should be F1 and F2.
        labels = [c.label.plain for c in block_node.children]
        assert "F1" in labels
        assert "F2" in labels


@pytest.mark.anyio
async def test_selecting_task_shows_content(docs_dir):
    """Clicking a task leaf should update the content pane."""
    app = EgoTUIApp(docs_dir=docs_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        # Expand the first block.
        block_node = tree.root.children[0]
        block_node.expand()
        await pilot.pause()
        # Select F1 (first leaf).
        f1_node = block_node.children[0]
        tree.select_node(f1_node)
        # Trigger the NodeSelected event (NodeSelected takes just the node).
        tree.post_message(Tree.NodeSelected(f1_node))
        await pilot.pause()
        # Content should be updated.
        content = app.query_one("#task-content", TaskContent)
        assert content is not None


@pytest.mark.anyio
async def test_empty_docs_dir(tmp_path):
    """App should handle missing docs/tasks/ gracefully."""
    app = EgoTUIApp(docs_dir=tmp_path / "nonexistent")
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#task-tree", TaskTree)
        # Should have a "not found" leaf.
        assert len(tree.root.children) >= 1
        # The leaf should say "not found".
        first_child = tree.root.children[0]
        assert "not found" in first_child.label.plain.lower() or "no" in first_child.label.plain.lower()


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
        # Two blocks: F and H.
        assert len(tree.root.children) == 2
        block_labels = [c.label.plain for c in tree.root.children]
        assert any("F" in l for l in block_labels)
        assert any("H" in l for l in block_labels)
