"""Ego TUI — textual application with task editor and check button.

Three-pane layout:
  Left:   task list (blocks + tasks, tree-style)
  Right:  task content (statement markdown rendered) + code editor + check button
  Bottom: check result output

Per ADR-0001 D13 (three entry-points), beads ego-trainer-x4f.1 (skeleton)
and ego-trainer-x4f.2 (task screen with editor + Проверить button).
"""

from __future__ import annotations

import re
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Markdown,
    Static,
    TextArea,
    Tree,
)


class TaskTree(Tree):
    """Tree widget showing blocks and tasks from docs/tasks/."""

    def __init__(self, docs_dir: Path | None = None):
        super().__init__("Tasks", id="task-tree")
        self._docs_dir = docs_dir or Path("docs/tasks")

    def on_mount(self) -> None:
        """Populate the tree from docs/tasks/."""
        self._populate()

    def _populate(self) -> None:
        """Scan docs/tasks/ and build the tree."""
        if not self._docs_dir.exists():
            self.root.add_leaf("(docs/tasks/ not found)")
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
            block_node = self.root.add(f"Block {label}", expand=False)
            for md in blocks[block_name]:
                stem = md.stem
                rest = stem[len("task_"):] if stem.startswith("task_") else stem
                task_id = rest.replace("_", ".").upper()
                block_node.add_leaf(task_id, data=md)


class TaskContent(Static):
    """Right pane: renders the task statement as markdown + code editor + check button."""

    def __init__(self):
        super().__init__(id="task-content")
        self._current_md_path: Path | None = None
        self._current_task_id: str = ""

    def compose(self) -> ComposeResult:
        yield Markdown("", id="task-md")
        yield Static("Code editor:", id="editor-label")
        yield TextArea.code_editor("", id="code-editor", language="python")
        yield Button("Проверить", id="check-button", variant="primary")
        yield Static("", id="check-result")

    def show_task(self, md_path: Path) -> None:
        """Load and render a task .md file, load student code into editor."""
        self._current_md_path = md_path
        # Derive task id from filename.
        stem = md_path.stem
        rest = stem[len("task_"):] if stem.startswith("task_") else stem
        self._current_task_id = rest.replace("_", ".").upper()

        # Show markdown (strip <details> blocks).
        if md_path.exists():
            content = md_path.read_text(encoding="utf-8")
            clean = re.sub(r"<details>.*?</details>", "", content, flags=re.DOTALL)
            self.query_one("#task-md", Markdown).update(clean)
        else:
            self.query_one("#task-md", Markdown).update(f"*File not found: {md_path}*")

        # Load student code into editor.
        py_path = md_path.with_suffix(".py")
        # Try tasks/<slug>/task_<id>.py first.
        student_py = md_path.parent / py_path.name
        if not student_py.exists():
            # Try tasks/ directory.
            normalized = self._current_task_id.replace(".", "_").lower()
            filename = f"task_{normalized}.py"
            tasks_dir = Path("tasks")
            if tasks_dir.exists():
                for p in tasks_dir.rglob(filename):
                    student_py = p
                    break

        editor = self.query_one("#code-editor", TextArea)
        if student_py.exists():
            editor.text = student_py.read_text(encoding="utf-8")
        else:
            # Load stub from .md if no student code yet.
            editor.text = "# No student code found. Start coding here:\n\npass\n"

        # Clear previous check result.
        self.query_one("#check-result", Static).update("")

    @property
    def current_task_id(self) -> str:
        return self._current_task_id

    @property
    def current_md_path(self) -> Path | None:
        return self._current_md_path


class EgoTUIApp(App):
    """Ego TUI — practice tasks with auto-checking.

    x4f.1: two-pane layout, task tree + content viewer.
    x4f.2: adds code editor + "Проверить" button + result display.
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
    #task-md {
        height: 40%;
    }
    #code-editor {
        height: 40%;
    }
    #check-button {
        margin: 1 0;
    }
    #check-result {
        border: solid $accent;
        padding: 1 2;
        max-height: 20%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("c", "check", "Check"),
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
        """When a leaf (task) is selected, show its content + editor."""
        node = event.node
        if node.data is not None and isinstance(node.data, Path):
            content = self.query_one("#task-content", TaskContent)
            content.show_task(node.data)

    @on(Button.Pressed, "#check-button")
    def on_check_button(self, event: Button.Pressed) -> None:
        """Run check when the 'Проверить' button is pressed."""
        self._run_check()

    def action_check(self) -> None:
        """Keyboard shortcut 'c' to run check."""
        self._run_check()

    def _run_check(self) -> None:
        """Run the checker on the current task and display results."""
        content = self.query_one("#task-content", TaskContent)
        task_id = content.current_task_id
        md_path = content.current_md_path
        if not md_path or not task_id:
            return

        editor = self.query_one("#code-editor", TextArea)
        student_code = editor.text

        result_widget = self.query_one("#check-result", Static)
        result_widget.update("Checking...")

        try:
            from ego.checker import format_check_result, run_check
            from ego.parser import parse_task_file

            task = parse_task_file(md_path)
            result = run_check(task, student_code)
            output = format_check_result(result)
            result_widget.update(output)
        except Exception as e:  # noqa: BLE001
            result_widget.update(f"Error: {e}")

    def action_refresh(self) -> None:
        """Refresh the task tree (re-scan docs/tasks/)."""
        tree = self.query_one("#task-tree", TaskTree)
        tree.root.remove_children()
        tree._populate()
        if tree.root.children:
            tree.root.children[0].expand()


def run(docs_dir: Path | None = None) -> int:
    """Launch the TUI app. Returns exit code."""
    app = EgoTUIApp(docs_dir=docs_dir)
    result = app.run()
    return 0 if result is None else 1
