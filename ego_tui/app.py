"""Ego TUI — textual application skeleton.

Two-pane layout:
  Left:  task list (blocks + tasks, tree-style)
  Right: task content (statement markdown rendered)

Per ADR-0001 D13 (three entry-points) and beads ego-trainer-x4f.1.
The actual task editor + "Проверить" button is x4f.2; this is the skeleton
with navigation and content rendering only.
"""

from __future__ import annotations

from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Markdown, Static, Tree
from textual.widgets.tree import TreeNode


class TaskTree(Tree):
    """Tree widget showing blocks and tasks from docs/tasks/."""

    def __init__(self, docs_dir: Path | None = None):
        super().__init__("Tasks", id="task-tree")
        self._docs_dir = docs_dir or Path("docs/tasks")

    def on_mount(self) -> None:
        """Populate the tree from docs/tasks/."""
        if not self._docs_dir.exists():
            self.root.add_leaf("(docs/tasks/ not found)")
            return

        # Group .md files by block.
        blocks: dict[str, list[Path]] = {}
        for md in sorted(self._docs_dir.rglob("task_*.md")):
            block = md.parent.name
            blocks.setdefault(block, []).append(md)

        for block_name in sorted(blocks):
            # Use first letter after "block_" as the block label.
            parts = block_name.split("_")
            label = parts[1].upper() if len(parts) >= 2 and parts[0] == "block" else block_name
            block_node = self.root.add(f"Block {label}", expand=False)
            for md in blocks[block_name]:
                # Derive task id from filename: task_f1.md -> F1.
                stem = md.stem  # task_f1
                rest = stem[len("task_"):] if stem.startswith("task_") else stem
                task_id = rest.replace("_", ".").upper()
                block_node.add_leaf(task_id, data=md)


class TaskContent(Static):
    """Right pane: renders the task statement as markdown."""

    def __init__(self):
        super().__init__(id="task-content")
        self._markdown = Markdown("", id="task-md")

    def compose(self) -> ComposeResult:
        yield self._markdown

    def show_task(self, md_path: Path) -> None:
        """Load and render a task .md file (stripping <details> blocks)."""
        if not md_path.exists():
            self._markdown.update(f"*File not found: {md_path}*")
            return
        content = md_path.read_text(encoding="utf-8")
        # Strip <details>...</details> (эталон) — student shouldn't see it.
        import re

        clean = re.sub(r"<details>.*?</details>", "", content, flags=re.DOTALL)
        self._markdown.update(clean)


class EgoTUIApp(App):
    """Ego TUI — practice tasks with auto-checking.

    Skeleton (x4f.1): two-pane layout, task tree + content viewer.
    Task editor and check button come in x4f.2.
    """

    TITLE = "Ego TUI"
    SUB_TITLE = "Practice tasks for junior developers"
    CSS = """
    #task-tree {
        width: 30%;
        dock: left;
        border: solid $primary;
    }
    #task-content {
        width: 70%;
        border: solid $primary;
        padding: 1 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, docs_dir: Path | None = None):
        super().__init__()
        self._docs_dir = docs_dir or Path("docs/tasks")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            TaskTree(self._docs_dir),
            TaskContent(),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Expand the first block on mount."""
        tree = self.query_one("#task-tree", TaskTree)
        if tree.root.children:
            tree.root.children[0].expand()

    @on(Tree.NodeSelected)
    def on_node_selected(self, event: Tree.NodeSelected) -> None:
        """When a leaf (task) is selected, show its content."""
        node = event.node
        if node.data is not None and isinstance(node.data, Path):
            content = self.query_one("#task-content", TaskContent)
            content.show_task(node.data)

    def action_refresh(self) -> None:
        """Refresh the task tree (re-scan docs/tasks/)."""
        tree = self.query_one("#task-tree", TaskTree)
        tree.clear()
        # Re-populate by re-mounting.
        tree.root.remove_children()
        # Re-run the mount logic.
        if not self._docs_dir.exists():
            tree.root.add_leaf("(docs/tasks/ not found)")
            return
        blocks: dict[str, list[Path]] = {}
        for md in sorted(self._docs_dir.rglob("task_*.md")):
            block = md.parent.name
            blocks.setdefault(block, []).append(md)
        for block_name in sorted(blocks):
            parts = block_name.split("_")
            label = (
                parts[1].upper()
                if len(parts) >= 2 and parts[0] == "block"
                else block_name
            )
            block_node = tree.root.add(f"Block {label}", expand=False)
            for md in blocks[block_name]:
                stem = md.stem
                rest = stem[len("task_"):] if stem.startswith("task_") else stem
                task_id = rest.replace("_", ".").upper()
                block_node.add_leaf(task_id, data=md)


def run(docs_dir: Path | None = None) -> int:
    """Launch the TUI app. Returns exit code."""
    app = EgoTUIApp(docs_dir=docs_dir)
    result = app.run()
    return 0 if result is None else 1
