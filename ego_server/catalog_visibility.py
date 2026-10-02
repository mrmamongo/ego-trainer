"""Reversible catalog visibility, independent of historical learner records."""

import sqlite3


ACTIVE_TASK_FILTER = (
    "tasks.archived = 0 AND NOT EXISTS "
    "(SELECT 1 FROM projects p WHERE p.id = tasks.project_id AND p.archived = 1)"
)


def activate_only_projects(conn: sqlite3.Connection, project_ids: list[str]) -> dict:
    """Select the visible projects without deleting content or learner history.

    The caller owns the transaction. Every selected project must already have
    tasks, so a failed/empty import cannot accidentally hide the whole catalog.
    Repeating the operation is safe; selecting an old project restores it.
    """
    selected = sorted(set(project_ids))
    if not selected:
        raise ValueError("at least one populated project must remain visible")
    for project_id in selected:
        project = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        count = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE project_id = ?", (project_id,)
        ).fetchone()[0]
        if project is None or count == 0:
            raise ValueError(f"project must exist and contain tasks: {project_id}")
    placeholders = ",".join("?" for _ in selected)
    conn.execute(
        f"UPDATE projects SET archived = CASE WHEN id IN ({placeholders}) THEN 0 ELSE 1 END",
        selected,
    )
    conn.execute(
        f"UPDATE tasks SET archived = CASE WHEN project_id IN ({placeholders}) THEN 0 ELSE 1 END",
        selected,
    )
    return {
        "active_projects": selected,
        "active_tasks": conn.execute("SELECT COUNT(*) FROM tasks WHERE archived = 0").fetchone()[0],
        "archived_tasks": conn.execute("SELECT COUNT(*) FROM tasks WHERE archived = 1").fetchone()[0],
    }
