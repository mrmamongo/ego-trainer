"""Content-repo sync pipeline (ADR-0016 D16.2, D16.5, D16.6).

PR 1: local sync only (``file://`` URL or local path).
PR 2 will add git clone/pull for ``https://`` URLs + cron + Docker.

Pipeline (per D16.2):
1. Resolve content-repo path from :class:`TasksRepoConfig`.
2. Walk the repo via :func:`ego.content_repo.discover_repo`.
3. Upsert ``projects`` / ``folders`` / ``tasks`` / ``task_versions``.
4. Apply SemVer policy (``declare`` vs ``auto_minor``) + breaking → stale.
5. Write a ``sync_log`` row with counts (added/updated/skipped/errors).

SemVer policy (per D16.6):
- ``content_hash`` unchanged → skip task.
- hash changed + file ``version`` strictly greater than DB → update.
- hash changed + version not bumped → sync error (task skipped, counted).
- ``breaking: true`` or major bump → mark prior progress ``stale``.
- ``auto_minor`` policy (legacy fixture) → silent minor bump (old behavior).

Theory cards (``lesson_*.md``, catalog mode only):
- lessons are upserted by id (update when ``content_hash`` changes);
- lessons of a synced project whose file disappeared are deleted;
- a duplicate lesson id (second card) is a sync error; an unknown
  ``theory`` id on a task only adds a warning to ``error_details``;
- task ``theory`` is metadata, not graded content: it is refreshed on
  every sync even when the task hash/version did not change.
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ego.catalog import (
    CONTENT_ID_RE,
    Folder,
    Project,
    RecommendedAfter,
    TaskFrontmatter,
    lesson_content_hash,
)
from ego.content_repo import (
    DiscoveredLesson,
    DiscoveredTask,
    discover_repo,
)
from ego.models import Task
from ego.parser import parse_task_file
from ego_server.content_config import TasksRepoConfig


# === Sync result ===


@dataclass
class SyncResult:
    """Outcome of one sync run — counts + per-task errors."""

    added: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)
    git_sha: str | None = None  # PR 2: git revision; PR 1: None
    started_at: str = ""
    finished_at: str = ""
    log_id: int | None = None  # sync_log row id
    # Theory cards: reported in the summary, not part of added/updated/skipped.
    lessons_added: int = 0
    lessons_updated: int = 0
    lessons_deleted: int = 0

    @property
    def status(self) -> str:
        """Aggregate status: ``success`` | ``partial`` | ``failed``."""
        if self.errors == 0:
            return "success"
        if self.added + self.updated + self.skipped > 0:
            return "partial"
        return "failed"

    @property
    def error_details_text(self) -> str:
        return "\n".join(self.error_details)


# === Public API ===


def sync_from_config(
    conn: sqlite3.Connection, config: TasksRepoConfig, *, source: str = "manual"
) -> SyncResult:
    """Sync content-repo into DB per ``config``.

    Args:
        conn: SQLite connection (row_factory = sqlite3.Row).
        config: :class:`TasksRepoConfig` with ``url`` (file:// or local path).
        source: ``'manual'`` | ``'cron'`` | ``'startup'`` — for sync_log.

    Returns:
        :class:`SyncResult` with counts and per-task errors.
    """
    if not config.url:
        raise ValueError("TasksRepoConfig.url is empty — nothing to sync from")
    repo_path = config.resolved_local_path
    return sync_from_path(conn, repo_path, source=source, repo_url=config.url)


def sync_from_path(
    conn: sqlite3.Connection,
    repo_path: Path,
    *,
    source: str = "manual",
    repo_url: str = "",
) -> SyncResult:
    """Sync a local content-repo directory into DB.

    Args:
        conn: SQLite connection.
        repo_path: path to content-repo root (catalog mode) or ``docs/tasks/`` (legacy).
        source: sync trigger source (for sync_log).
        repo_url: original URL (for sync_log; may differ from repo_path for git URLs in PR 2).

    Returns:
        :class:`SyncResult`.
    """
    started = _now_iso()
    result = (
        SyncResult(started_at=started, repo_url=repo_url)
        if False
        else SyncResult(started_at=started)
    )
    # Note: repo_url stored via sync_log row below.
    log_id = _start_sync_log(conn, started=started, source=source, repo_url=repo_url)
    result.log_id = log_id

    try:
        catalog = discover_repo(Path(repo_path))
    except Exception as e:  # noqa: BLE001 — top-level failure
        result.errors += 1
        result.error_details.append(f"discover_repo failed: {e}")
        _finish_sync_log(conn, log_id, result, git_sha=None)
        return result

    # Upsert projects, folders, lessons, tasks.
    for proj in catalog.projects:
        _upsert_project(conn, proj.project)
        synced_lesson_ids: set[str] = set()
        for folder in proj.folders:
            _upsert_folder(conn, folder.folder, proj.project.id)
            for lesson in folder.lessons:
                _upsert_lesson(conn, lesson, result, synced_lesson_ids)
            for dtask in folder.tasks:
                _upsert_discovered_task(conn, dtask, proj.project, folder.folder, result)
        _delete_stale_lessons(conn, proj.project.id, synced_lesson_ids, result)

    _finish_sync_log(conn, log_id, result, git_sha=None)
    return result


# === Project / Folder upsert ===


def _upsert_project(conn: sqlite3.Connection, project: Project) -> None:
    """Insert or update a row in ``projects`` (idempotent by id)."""
    now = _now_iso()
    recommended_json = _dump_recommended(project.recommended_after)
    existing = conn.execute("SELECT id FROM projects WHERE id = ?", (project.id,)).fetchone()
    if existing is None:
        conn.execute(
            """INSERT INTO projects
            (id, name, description, version, "order", default_locale, tags,
             version_policy, recommended_after, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project.id,
                project.name,
                project.description,
                project.version,
                project.order,
                project.default_locale,
                _dump_tags(project.tags),
                project.version_policy,
                recommended_json,
                now,
                now,
            ),
        )
        return
    conn.execute(
        """UPDATE projects SET
        name = ?, description = ?, version = ?, "order" = ?, default_locale = ?,
        tags = ?, version_policy = ?, recommended_after = ?, updated_at = ?
        WHERE id = ?""",
        (
            project.name,
            project.description,
            project.version,
            project.order,
            project.default_locale,
            _dump_tags(project.tags),
            project.version_policy,
            recommended_json,
            now,
            project.id,
        ),
    )


def _upsert_folder(conn: sqlite3.Connection, folder: Folder, project_id: str) -> None:
    """Insert or update a row in ``folders`` (idempotent by (id, project_id))."""
    now = _now_iso()
    existing = conn.execute(
        "SELECT id FROM folders WHERE id = ? AND project_id = ?",
        (folder.id, project_id),
    ).fetchone()
    level = folder.level if folder.level is not None else None
    if existing is None:
        conn.execute(
            """INSERT INTO folders
            (id, project_id, code, name, description, "order", level,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                folder.id,
                project_id,
                folder.code,
                folder.name,
                folder.description,
                folder.order,
                level,
                now,
                now,
            ),
        )
        return
    conn.execute(
        """UPDATE folders SET
        code = ?, name = ?, description = ?, "order" = ?, level = ?, updated_at = ?
        WHERE id = ? AND project_id = ?""",
        (
            folder.code,
            folder.name,
            folder.description,
            folder.order,
            level,
            now,
            folder.id,
            project_id,
        ),
    )


# === Lesson (theory card) upsert ===


def _upsert_lesson(
    conn: sqlite3.Connection,
    lesson: DiscoveredLesson,
    result: SyncResult,
    synced_ids: set[str],
) -> None:
    """Upsert one discovered ``lesson_*.md`` (idempotent by id).

    A file that failed to parse, a lesson id that was already seen in this
    repo (duplicate), or an id that is not URL-safe is a sync error — the
    card is skipped, counted, and never written.
    """
    where = lesson.md_path.name
    if lesson.frontmatter is None:
        result.errors += 1
        result.error_details.append(f"LESSON {where}: {lesson.error}")
        return
    fm = lesson.frontmatter
    if not re.fullmatch(CONTENT_ID_RE, fm.id):
        result.errors += 1
        result.error_details.append(
            f"LESSON {where}: invalid id {fm.id!r} "
            f"(expected {CONTENT_ID_RE}); skipping"
        )
        return
    if fm.id in synced_ids:
        result.errors += 1
        result.error_details.append(
            f"LESSON {fm.id}: duplicate lesson id (second file {where}); skipping"
        )
        return
    synced_ids.add(fm.id)

    now = _now_iso()
    content_hash = lesson_content_hash(fm, lesson.body_md)
    existing = conn.execute(
        "SELECT content_hash FROM lessons WHERE id = ?", (fm.id,)
    ).fetchone()
    if existing is None:
        conn.execute(
            """INSERT INTO lessons
            (id, project_id, folder_id, title, "order", version, content_hash,
             body_md, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                fm.id,
                lesson.project_id,
                lesson.folder_id,
                fm.title,
                fm.order,
                fm.version,
                content_hash,
                lesson.body_md,
                now,
                now,
            ),
        )
        result.lessons_added += 1
        return
    # Lessons carry no SemVer gate: any change is applied in place.
    if existing["content_hash"] == content_hash:
        return
    conn.execute(
        """UPDATE lessons SET
        project_id = ?, folder_id = ?, title = ?, "order" = ?, version = ?,
        content_hash = ?, body_md = ?, updated_at = ?
        WHERE id = ?""",
        (
            lesson.project_id,
            lesson.folder_id,
            fm.title,
            fm.order,
            fm.version,
            content_hash,
            lesson.body_md,
            now,
            fm.id,
        ),
    )
    result.lessons_updated += 1


def _delete_stale_lessons(
    conn: sqlite3.Connection,
    project_id: str,
    synced_ids: set[str],
    result: SyncResult,
) -> None:
    """Delete lessons of ``project_id`` whose ``lesson_*.md`` disappeared."""
    existing_ids = [
        row["id"]
        for row in conn.execute(
            "SELECT id FROM lessons WHERE project_id = ?", (project_id,)
        ).fetchall()
    ]
    stale = [lesson_id for lesson_id in existing_ids if lesson_id not in synced_ids]
    if not stale:
        return
    conn.executemany("DELETE FROM lessons WHERE id = ?", [(i,) for i in stale])
    result.lessons_deleted += len(stale)


# === Task upsert (the core of sync) ===


def _upsert_discovered_task(
    conn: sqlite3.Connection,
    dtask: DiscoveredTask,
    project: Project,
    folder: Folder,
    result: SyncResult,
) -> None:
    """Parse + upsert one discovered task.

    Uses :func:`ego.parser.parse_task_file` for the heavy lifting (statement,
    stub, solution, content_hash). Frontmatter (if present) overrides
    version/level/tags/breaking from the parser defaults.
    """
    try:
        task = parse_task_file(dtask.md_path)
    except Exception as e:  # noqa: BLE001 — per-task errors don't abort sync
        result.errors += 1
        result.error_details.append(f"PARSE {dtask.md_path.name}: {e}")
        return

    # Apply frontmatter overrides (D16.6: frontmatter is source of truth).
    if dtask.frontmatter is not None:
        task = _apply_frontmatter(task, dtask.frontmatter)
    theory = _task_theory(dtask.frontmatter)

    # Attach catalog FKs.
    task_version_policy = project.version_policy

    outcome = _upsert_task_row(
        conn,
        task,
        folder_id=folder.id,
        project_id=project.id,
        version_policy=task_version_policy,
        declared_breaking=task.extra.get("breaking", False),
        theory=theory,
    )
    if outcome == "imported":
        result.added += 1
    elif outcome == "updated":
        result.updated += 1
    elif outcome == "skipped":
        result.skipped += 1
    elif outcome == "error":
        result.errors += 1
        result.error_details.append(
            f"VERSION {task.id}: content changed but version not bumped "
            f"(file v{task.version} <= DB v); skipping"
        )

    # Lessons are synced after every task of the project, but validate ids
    # up front: theory is only advisory, so a bad id must never fail the task.
    for lesson_id in theory:
        if not re.fullmatch(CONTENT_ID_RE, lesson_id):
            result.error_details.append(
                f"THEORY {task.id}: invalid lesson id {lesson_id!r} "
                f"(expected {CONTENT_ID_RE})"
            )
            continue
        known = conn.execute("SELECT 1 FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
        if known is None:
            result.error_details.append(
                f"THEORY {task.id}: lesson '{lesson_id}' not found; warning only"
            )


def _task_theory(fm: TaskFrontmatter | None) -> list[str]:
    """Ordered, de-duplicated lesson ids from task frontmatter."""
    if fm is None:
        return []
    out: list[str] = []
    for lesson_id in fm.theory:
        lesson_id = str(lesson_id).strip()
        if lesson_id and lesson_id not in out:
            out.append(lesson_id)
    return out


def _apply_frontmatter(task: Task, fm: TaskFrontmatter) -> Task:
    """Override task fields from frontmatter (D16.6: frontmatter is truth)."""
    task.version = fm.version
    task.level = fm.level
    task.tags = list(fm.tags)
    if fm.title:
        task.title = fm.title
    if fm.id:
        task.id = fm.id
        task.task_id = fm.id
    if fm.breaking:
        task.extra["breaking"] = True
    return task


def _upsert_task_row(
    conn: sqlite3.Connection,
    task: Task,
    *,
    folder_id: str,
    project_id: str,
    version_policy: str,
    declared_breaking: bool,
    theory: list[str] | None = None,
) -> str:
    """Insert/update ``tasks`` + ``task_versions`` per SemVer policy.

    ``theory`` (lesson ids) is not graded content: it is written on every
    call, and a theory-only change does not require a version bump.

    Returns ``"imported"`` | ``"updated"`` | ``"skipped"`` | ``"error"``.
    """
    now = _now_iso()
    theory_json = _dump_tags(theory or [])
    existing = conn.execute(
        "SELECT id, version, content_hash, theory, block, slug, md_path, folder_id, project_id FROM tasks WHERE id = ?",
        (task.id,),
    ).fetchone()

    if existing is None:
        # Insert new task.
        conn.execute(
            """INSERT INTO tasks
            (id, block, slug, task_id, title, level, tags, version,
             content_hash, breaking, md_path, folder_id, project_id, theory,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.id,
                task.block,
                task.slug,
                task.task_id,
                task.title,
                task.level,
                _dump_tags(task.tags),
                task.version,
                task.content_hash,
                1 if declared_breaking else 0,
                str(task.md_path),
                folder_id,
                project_id,
                theory_json,
                now,
                now,
            ),
        )
        conn.execute(
            """INSERT INTO task_versions
            (task_id, version, content_hash, breaking, md_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                task.id,
                task.version,
                task.content_hash,
                1 if declared_breaking else 0,
                str(task.md_path),
                now,
            ),
        )
        return "imported"

    # Existing task — compare hash.
    if existing["content_hash"] == task.content_hash and (
        version_policy == "auto_minor" or task.version == existing["version"]
    ):
        # Metadata refresh: theory links and catalog placement (moving a task to
        # another folder) never affect grading, so they need no version bump.
        placement = (task.block, task.slug, str(task.md_path), folder_id, project_id)
        current = (
            existing["block"], existing["slug"], existing["md_path"],
            existing["folder_id"], existing["project_id"],
        )
        if (existing["theory"] or "[]") != theory_json or current != placement:
            conn.execute(
                """UPDATE tasks SET theory = ?, block = ?, slug = ?, md_path = ?,
                folder_id = ?, project_id = ?, updated_at = ? WHERE id = ?""",
                (theory_json, *placement, now, task.id),
            )
            return "updated"
        return "skipped"

    # Content changed — resolve new version per policy.
    old_version = existing["version"]
    if version_policy == "auto_minor":
        new_version = _bump_minor(old_version)
    else:
        # declare policy: file version must be strictly greater than DB.
        if not _semver_gt(task.version, old_version):
            return "error"
        new_version = task.version

    is_breaking = declared_breaking or _is_major_bump(old_version, new_version)

    conn.execute(
        """UPDATE tasks SET
        block = ?, slug = ?, task_id = ?, title = ?, level = ?, tags = ?,
        version = ?, content_hash = ?, breaking = ?, md_path = ?,
        folder_id = ?, project_id = ?, theory = ?, updated_at = ?
        WHERE id = ?""",
        (
            task.block,
            task.slug,
            task.task_id,
            task.title,
            task.level,
            _dump_tags(task.tags),
            new_version,
            task.content_hash,
            1 if is_breaking else 0,
            str(task.md_path),
            folder_id,
            project_id,
            theory_json,
            now,
            task.id,
        ),
    )
    conn.execute(
        """INSERT OR REPLACE INTO task_versions
        (task_id, version, content_hash, breaking, md_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (task.id, new_version, task.content_hash, 1 if is_breaking else 0, str(task.md_path), now),
    )

    # Breaking change → mark prior progress stale (D3/D10).
    if is_breaking:
        _mark_progress_stale(conn, task.id)

    return "updated"


# === sync_log ===


def _start_sync_log(conn: sqlite3.Connection, *, started: str, source: str, repo_url: str) -> int:
    """Insert a ``running`` sync_log row and return its id."""
    cur = conn.execute(
        """INSERT INTO sync_log
        (started_at, finished_at, source, repo_url, git_sha, status,
         added, updated, skipped, errors, error_details)
        VALUES (?, NULL, ?, ?, NULL, 'running', 0, 0, 0, 0, '')""",
        (started, source, repo_url),
    )
    return cur.lastrowid


def _finish_sync_log(
    conn: sqlite3.Connection, log_id: int, result: SyncResult, *, git_sha: str | None
) -> None:
    """Update the sync_log row with final counts + status."""
    finished = _now_iso()
    conn.execute(
        """UPDATE sync_log SET
        finished_at = ?, git_sha = ?, status = ?,
        added = ?, updated = ?, skipped = ?, errors = ?, error_details = ?
        WHERE id = ?""",
        (
            finished,
            git_sha,
            result.status,
            result.added,
            result.updated,
            result.skipped,
            result.errors,
            result.error_details_text,
            log_id,
        ),
    )
    result.finished_at = finished


# === Helpers ===


def _dump_tags(tags: list[str]) -> str:
    """Serialize tags list as a JSON array string (matches schema ``tags`` column)."""
    return json.dumps(tags, ensure_ascii=False)


def _dump_recommended(rec: RecommendedAfter | None) -> str | None:
    """Serialize ``recommended_after`` as JSON (``None`` when not declared)."""
    if rec is None:
        return None
    return rec.model_dump_json()


def _bump_minor(version: str) -> str:
    """Bump minor: ``'1.0.0'`` -> ``'1.1.0'``. Falls back to ``'1.0.0'``."""
    parts = version.split(".")
    if len(parts) != 3:
        return "1.0.0"
    try:
        major, minor, _patch = (int(p) for p in parts)
    except ValueError:
        return "1.0.0"
    return f"{major}.{minor + 1}.0"


def _semver_gt(a: str, b: str) -> bool:
    """Return True if SemVer ``a`` > ``b`` (strictly greater)."""
    pa = _parse_semver(a)
    pb = _parse_semver(b)
    if pa is None or pb is None:
        # Non-SemVer strings: fall back to string comparison.
        return a > b
    return pa > pb


def _parse_semver(v: str) -> tuple[int, int, int] | None:
    """Parse ``'1.2.3'`` → ``(1, 2, 3)``. Returns None if not SemVer."""
    parts = v.split(".")
    if len(parts) != 3:
        return None
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def _is_major_bump(old: str, new: str) -> bool:
    """True if major component increased (e.g. ``1.x`` → ``2.x``)."""
    po = _parse_semver(old)
    pn = _parse_semver(new)
    if po is None or pn is None:
        return False
    return pn[0] > po[0]


def _mark_progress_stale(conn: sqlite3.Connection, task_id: str) -> None:
    """Mark all progress rows for ``task_id`` as ``stale`` (D3/D10)."""
    conn.execute(
        "UPDATE progress SET status = 'stale' WHERE task_id = ?",
        (task_id,),
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
