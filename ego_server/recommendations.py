"""Soft course recommendations + exam-kind breakdown (pure DB helpers).

A project may declare in ``project.yaml``::

    recommended_after:
      project: xl-a
      min_passed: 21          # passed tasks in that project
      min_per_kind: 6         # optional: at least N passed of each kind tag
      note: "Курс ООП рекомендуем начинать после экзамена XL-A"

The recommendation is advisory only: it is stored by sync in
``projects.recommended_after`` (JSON) and reported by ``GET /projects``.
Nothing here can block a task, a check or a project.

Kinds are task tags from ``bug`` / ``modify`` / ``new`` (XL-A carries them);
every other tag lands in the free-form ``tags`` bucket of the breakdown.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field

from ego_server.catalog_visibility import ACTIVE_TASK_FILTER


#: Task kinds of the exam breakdown (``GET /progress/{student}/breakdown``).
KIND_TAGS: tuple[str, ...] = ("bug", "modify", "new")

#: Statuses that count as a passed task (``stale`` does not).
PASSED_STATUSES: tuple[str, ...] = ("passed",)


@dataclass
class RecommendedAfter:
    """Decoded ``projects.recommended_after``."""

    project: str
    min_passed: int = 0
    min_per_kind: int | None = None
    note: str = ""

    def as_dict(self) -> dict:
        return {
            "project": self.project,
            "min_passed": self.min_passed,
            "min_per_kind": self.min_per_kind,
            "note": self.note,
        }


@dataclass
class Readiness:
    """Student progress against one :class:`RecommendedAfter`."""

    met: bool
    passed: int
    required: int
    per_kind: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "met": self.met,
            "passed": self.passed,
            "required": self.required,
            "per_kind": dict(self.per_kind),
        }


def decode_recommended(raw: str | None) -> RecommendedAfter | None:
    """Parse the JSON column; malformed/empty values mean "no recommendation"."""
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    project = str(data.get("project") or "").strip()
    if not project:
        return None
    try:
        min_passed = max(int(data.get("min_passed") or 0), 0)
    except (TypeError, ValueError):
        min_passed = 0
    raw_per_kind = data.get("min_per_kind")
    min_per_kind: int | None = None
    if raw_per_kind is not None:
        try:
            min_per_kind = max(int(raw_per_kind), 0)
        except (TypeError, ValueError):
            min_per_kind = None
    return RecommendedAfter(
        project=project,
        min_passed=min_passed,
        min_per_kind=min_per_kind,
        note=str(data.get("note") or ""),
    )


def passed_task_ids(db: sqlite3.Connection, student_id: str) -> set[str]:
    """Tasks the student has passed at their current (non-archived) version.

    A task counts once even if several passed rows exist for it.
    """
    rows = db.execute(
        f"""SELECT DISTINCT p.task_id
            FROM progress p
            JOIN tasks ON tasks.id = p.task_id
            WHERE p.student_id = ?
              AND p.version = tasks.version
              AND lower(p.status) IN ({",".join("?" for _ in PASSED_STATUSES)})
              AND {ACTIVE_TASK_FILTER}""",
        (student_id, *PASSED_STATUSES),
    ).fetchall()
    return {row[0] for row in rows}


def project_tasks(db: sqlite3.Connection, project_id: str) -> list[tuple[str, list[str]]]:
    """``(task_id, tags)`` of the visible tasks of one project."""
    return _tasks_where(db, "tasks.project_id = ?", (project_id,))


def compute_readiness(
    rec: RecommendedAfter,
    tags_by_task: list[tuple[str, list[str]]],
    passed: set[str],
) -> Readiness:
    """Readiness math for one recommendation (no I/O).

    ``tags_by_task`` = tasks of ``rec.project``; ``passed`` = passed task ids
    of the student. ``met`` needs ``min_passed`` AND, when ``min_per_kind``
    is set, at least that many passed tasks in every kind tag.
    """
    kinds = list(KIND_TAGS) if rec.min_per_kind is not None else []
    passed_count = sum(1 for task_id, _ in tags_by_task if task_id in passed)
    per_kind: dict[str, int] = {}
    for kind in kinds:
        per_kind[kind] = sum(
            1 for task_id, tags in tags_by_task if task_id in passed and kind in tags
        )
    met = passed_count >= rec.min_passed and all(
        count >= (rec.min_per_kind or 0) for count in per_kind.values()
    )
    return Readiness(met=met, passed=passed_count, required=rec.min_passed, per_kind=per_kind)


def list_projects(db: sqlite3.Connection, student_id: str) -> list[dict]:
    """Visible projects with the recommendation + this student's readiness."""
    rows = db.execute(
        """SELECT id, name, "order" AS ord, recommended_after FROM projects
           WHERE archived = 0 ORDER BY "order", id"""
    ).fetchall()
    passed = passed_task_ids(db, student_id)
    out: list[dict] = []
    for row in rows:
        rec = decode_recommended(row["recommended_after"])
        readiness = None
        if rec is not None:
            readiness = compute_readiness(rec, project_tasks(db, rec.project), passed).as_dict()
        out.append(
            {
                "id": row["id"],
                "name": row["name"],
                "order": row["ord"],
                "recommended_after": rec.as_dict() if rec is not None else None,
                "readiness": readiness,
            }
        )
    return out


def compute_breakdown(
    tags_by_task: list[tuple[str, list[str]]], passed: set[str]
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    """``(kinds, tags)`` counters for a task set (no I/O)."""
    kinds = {kind: {"passed": 0, "total": 0} for kind in KIND_TAGS}
    others: dict[str, dict[str, int]] = {}
    for task_id, tags in tags_by_task:
        is_passed = task_id in passed
        unique_tags = list(dict.fromkeys(tags))
        for tag in unique_tags:
            if tag in kinds:
                bucket = kinds[tag]
                bucket["total"] += 1
                bucket["passed"] += 1 if is_passed else 0
            elif tag not in KIND_TAGS:
                bucket = others.setdefault(tag, {"passed": 0, "total": 0})
                bucket["total"] += 1
                bucket["passed"] += 1 if is_passed else 0
    return kinds, others


def breakdown(db: sqlite3.Connection, student_id: str, project: str | None) -> dict:
    """Exam breakdown of ``project`` (or of everything visible) for a student."""
    if project:
        tasks = project_tasks(db, project)
    else:
        tasks = _tasks_where(db, "1 = 1", ())
    kinds, tags = compute_breakdown(tasks, passed_task_ids(db, student_id))
    return {"project": project, "kinds": kinds, "tags": tags}


def _tasks_where(
    db: sqlite3.Connection, condition: str, params: tuple
) -> list[tuple[str, list[str]]]:
    """``(task_id, tags)`` of visible tasks matching ``condition``."""
    rows = db.execute(
        f"SELECT tasks.id, tasks.tags FROM tasks WHERE {condition} AND {ACTIVE_TASK_FILTER}",
        params,
    ).fetchall()
    out: list[tuple[str, list[str]]] = []
    for row in rows:
        try:
            tags = json.loads(row["tags"]) if row["tags"] else []
        except (TypeError, ValueError):
            tags = []
        out.append((row["id"], [str(t) for t in tags if t]))
    return out
