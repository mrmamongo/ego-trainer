"""Admin router — content-repo sync (ADR-0016 D16.2, D16.4).

PR 1: local sync only (``POST /admin/sync-tasks`` with a local path).
PR 2 will add git URL support + cron-triggered sync.

All endpoints require ``admin`` role (per ADR-0001 D8).
"""

from __future__ import annotations

import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from ego_server.auth import generate_user_id, hash_password
from ego_server.deps import DbDep, require_role
from ego_server.models import (
    CatalogDTO,
    CatalogFolderDTO,
    CatalogProjectDTO,
    CatalogTaskDTO,
    CreateUserRequest,
    OverviewCounts,
    OverviewDTO,
    ResetPasswordRequest,
    StudioValidateRequest,
    StudioValidateResponse,
    StudentSummaryDTO,
    SyncLogRow,
    SyncResultDTO,
    SyncTasksRequest,
    TaskStudioDTO,
    UpdateRoleRequest,
)
from ego_server.authoring import (
    contained_path,
    is_writable,
    resolve_root,
    safe_config,
)
from ego_server.sync import sync_from_path

router = APIRouter()


# === Mentor ops: student progress tracking ===


@router.get(
    "/students",
    response_model=list[StudentSummaryDTO],
    dependencies=[Depends(require_role("mentor", "admin"))],
)
async def list_students(db: DbDep) -> list[StudentSummaryDTO]:
    """List all students with their progress summary."""
    rows = db.execute(
        """SELECT s.id, s.username, s.role,
                  COUNT(p.task_id) AS tasks_total,
                  SUM(CASE WHEN p.status = 'passed' THEN 1 ELSE 0 END) AS tasks_passed,
                  SUM(CASE WHEN p.status = 'partial' THEN 1 ELSE 0 END) AS tasks_partial,
                  SUM(CASE WHEN p.status IN ('failed', 'error', 'timeout') THEN 1 ELSE 0 END) AS tasks_failed,
                  MAX(p.last_run_at) AS last_activity
           FROM students s
           LEFT JOIN progress p ON p.student_id = s.id
           WHERE s.role = 'student'
           GROUP BY s.id, s.username, s.role
           ORDER BY s.username"""
    ).fetchall()
    return [
        StudentSummaryDTO(
            student_id=r["id"],
            username=r["username"],
            role=r["role"],
            tasks_total=r["tasks_total"],
            tasks_passed=r["tasks_passed"] or 0,
            tasks_partial=r["tasks_partial"] or 0,
            tasks_failed=r["tasks_failed"] or 0,
            last_activity=r["last_activity"],
        )
        for r in rows
    ]


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def create_user(body: CreateUserRequest, db: DbDep) -> dict:
    """Create a new user (student/mentor/admin)."""
    existing = db.execute("SELECT id FROM students WHERE username = ?", (body.username,)).fetchone()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    user_id = generate_user_id()
    pwd_hash = hash_password(body.password)

    db.execute(
        "INSERT INTO students (id, username, role, password_hash, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, body.username, body.role, pwd_hash, datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    return {"id": user_id, "username": body.username, "role": body.role}


@router.put(
    "/users/{user_id}/role",
    dependencies=[Depends(require_role("admin"))],
)
async def update_user_role(user_id: str, body: UpdateRoleRequest, db: DbDep) -> dict:
    """Change a user's role."""
    row = db.execute("SELECT id FROM students WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.execute("UPDATE students SET role = ? WHERE id = ?", (body.role, user_id))
    db.commit()
    return {"id": user_id, "role": body.role}


@router.put(
    "/users/{user_id}/password",
    dependencies=[Depends(require_role("admin"))],
)
async def reset_user_password(user_id: str, body: ResetPasswordRequest, db: DbDep) -> dict:
    """Reset a user's password."""
    row = db.execute("SELECT id FROM students WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    pwd_hash = hash_password(body.password)
    db.execute("UPDATE students SET password_hash = ? WHERE id = ?", (pwd_hash, user_id))
    db.commit()
    return {"id": user_id, "password_reset": True}


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_user(user_id: str, db: DbDep) -> None:
    """Delete a user and their progress."""
    row = db.execute("SELECT id FROM students WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.execute("DELETE FROM progress WHERE student_id = ?", (user_id,))
    db.execute("DELETE FROM runs WHERE student_id = ?", (user_id,))
    db.execute("DELETE FROM students WHERE id = ?", (user_id,))
    db.commit()


@router.post(
    "/sync-tasks",
    response_model=SyncResultDTO,
    dependencies=[Depends(require_role("admin"))],
)
async def sync_tasks(req: SyncTasksRequest, db: DbDep) -> SyncResultDTO:
    """Sync content-repo at ``req.path`` into DB (PR 1: local path only).

    Triggers a full walk + upsert cycle. Returns counts (added/updated/
    skipped/errors) and a ``sync_log`` row id.

    Per ADR-0016 D16.5: ``path`` may be a local filesystem path or a
    ``file://`` URL. Git remote sync (``https://``) is implemented in PR 2.
    """
    repo_path = _resolve_path(req.path)
    if not repo_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"path not found or not a directory: {repo_path}",
        )

    result = sync_from_path(db, repo_path, source=req.source, repo_url=str(repo_path))
    db.commit()

    return _to_dto(result, repo_url=str(repo_path))


@router.get(
    "/sync/log",
    response_model=list[SyncLogRow],
    dependencies=[Depends(require_role("admin", "mentor"))],
)
async def get_sync_log(db: DbDep, limit: int = 50) -> list[SyncLogRow]:
    """Return recent sync_log rows (newest first, default 50)."""
    if limit < 1 or limit > 500:
        limit = 50
    rows = db.execute(
        """SELECT id, started_at, finished_at, source, repo_url, git_sha,
                  status, added, updated, skipped, errors, error_details
           FROM sync_log ORDER BY id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    return [SyncLogRow(**dict(r)) for r in rows]


@router.get(
    "/sync/status",
    response_model=SyncLogRow | None,
    dependencies=[Depends(require_role("admin", "mentor"))],
)
async def get_sync_status(db: DbDep) -> SyncLogRow | None:
    """Return the most recent sync_log row (or null if no syncs yet)."""
    row = db.execute(
        """SELECT id, started_at, finished_at, source, repo_url, git_sha,
                  status, added, updated, skipped, errors, error_details
           FROM sync_log ORDER BY id DESC LIMIT 1"""
    ).fetchone()
    if row is None:
        return None
    return SyncLogRow(**dict(row))


@router.get(
    "/overview",
    response_model=OverviewDTO,
    dependencies=[Depends(require_role("mentor", "admin"))],
)
async def get_overview(db: DbDep) -> OverviewDTO:
    """Aggregate snapshot: server status, catalog/student counts, latest sync.

    Returns a stable JSON shape for the admin/mentor dashboard. ``server`` is
    always ``"ok"`` (the endpoint would not be reachable otherwise). Counts
    come from the current DB state; ``latest_sync`` is the newest
    ``sync_log`` row or ``None`` when no sync has ever run.
    """
    projects = db.execute("SELECT COUNT(*) AS n FROM projects").fetchone()["n"]
    folders = db.execute("SELECT COUNT(*) AS n FROM folders").fetchone()["n"]
    tasks = db.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
    students = db.execute("SELECT COUNT(*) AS n FROM students WHERE role = 'student'").fetchone()[
        "n"
    ]

    sync_row = db.execute(
        """SELECT id, started_at, finished_at, source, repo_url, git_sha,
                  status, added, updated, skipped, errors, error_details
           FROM sync_log ORDER BY id DESC LIMIT 1"""
    ).fetchone()
    latest_sync = SyncLogRow(**dict(sync_row)) if sync_row is not None else None

    return OverviewDTO(
        server="ok",
        counts=OverviewCounts(
            projects=projects,
            folders=folders,
            tasks=tasks,
            students=students,
        ),
        latest_sync=latest_sync,
    )


@router.get(
    "/catalog",
    response_model=CatalogDTO,
    dependencies=[Depends(require_role("mentor", "admin"))],
)
async def get_catalog(db: DbDep, q: str | None = None) -> CatalogDTO:
    """Browse the catalog hierarchy: projects -> folders -> tasks.

    Reads the existing ``projects``/``folders``/``tasks`` tables and returns
    a deterministic, nested snapshot. Ordering is stable:

    * projects by (``order``, ``id``)
    * folders  by (``order``, ``id``)
    * tasks    by (``task_id``, ``id``)

    Only columns that already exist on the tables are exposed — no schema
    is invented. ``breaking`` is normalised from the 0/1 int to a bool.

    Optional ``q`` performs a case-insensitive substring match against
    project/folder/task identifiers and names (project ``id``/``name``,
    folder ``id``/``code``/``name``, task ``id``/``task_id``/``title``/
    ``slug``/``md_path``). Unmatched leaves are pruned, but ancestors of
    any match are retained so the hierarchy stays connected. An empty DB
    (or a ``q`` that matches nothing) yields ``{"projects": []}``.
    """
    projects_rows = db.execute(
        'SELECT id, name, "order", version FROM projects ORDER BY "order", id'
    ).fetchall()
    folders_rows = db.execute(
        'SELECT id, project_id, code, name, "order", level '
        'FROM folders ORDER BY "order", id, project_id'
    ).fetchall()
    tasks_rows = db.execute(
        "SELECT id, task_id, title, block, slug, level, version, breaking, "
        "md_path, folder_id, project_id FROM tasks ORDER BY task_id, id"
    ).fetchall()

    tasks_by_folder: dict[str, list[dict]] = {}
    for r in tasks_rows:
        t = dict(r)
        t["breaking"] = bool(t["breaking"])
        tasks_by_folder.setdefault(t["folder_id"] or "", []).append(t)

    needle = (q or "").strip().lower()
    searching = needle != ""

    def task_hits(t: dict) -> bool:
        if not searching:
            return True
        return (
            needle in " ".join([t["id"], t["task_id"], t["title"], t["slug"], t["md_path"]]).lower()
        )

    def folder_hits(f: dict) -> bool:
        if not searching:
            return True
        return needle in " ".join([f["id"], f["code"], f["name"]]).lower()

    def project_hits(p: dict) -> bool:
        if not searching:
            return True
        return needle in " ".join([p["id"], p["name"]]).lower()

    # Direct (self) match flags, computed once.
    proj_direct = {p["id"]: project_hits(dict(p)) for p in projects_rows}
    folder_direct = {f["id"]: folder_hits(dict(f)) for f in folders_rows}
    # Does any task in this folder match directly?
    folder_has_match_task = {
        fid: any(task_hits(t) for t in ts) for fid, ts in tasks_by_folder.items()
    }

    # Subtree-aware retention: a node is kept if it matches, any ancestor
    # matches, or any descendant matches. This keeps the hierarchy connected
    # both upward (ancestors of a matching task) and downward (the full
    # subtree of a matching project/folder).
    projects_out: list[CatalogProjectDTO] = []
    for p in projects_rows:
        p = dict(p)
        pm = proj_direct[p["id"]]
        folders_out: list[CatalogFolderDTO] = []
        for f in folders_rows:
            if f["project_id"] != p["id"]:
                continue
            f = dict(f)
            fm = folder_direct[f["id"]]
            keep_folder = pm or fm or folder_has_match_task.get(f["id"], False)
            if not keep_folder:
                continue
            kept_tasks: list[CatalogTaskDTO] = []
            for t in tasks_by_folder.get(f["id"], []):
                if pm or fm or task_hits(t):
                    kept_tasks.append(CatalogTaskDTO(**t))
            folders_out.append(
                CatalogFolderDTO(
                    id=f["id"],
                    project_id=f["project_id"],
                    code=f["code"],
                    name=f["name"],
                    order=f["order"],
                    level=f["level"],
                    tasks=kept_tasks,
                )
            )
        if not (pm or folders_out):
            continue
        projects_out.append(
            CatalogProjectDTO(
                id=p["id"],
                name=p["name"],
                order=p["order"],
                version=p["version"],
                folders=folders_out,
            )
        )

    return CatalogDTO(projects=projects_out)


# === Task Studio read (GET /admin/tasks/{task_id}/studio) ===


@router.get(
    "/tasks/{task_id}/studio",
    response_model=TaskStudioDTO,
    dependencies=[Depends(require_role("mentor", "admin"))],
)
async def get_task_studio(task_id: str, db: DbDep) -> TaskStudioDTO:
    """Read a task's canonical markdown + .solution.py/.tests.py sidecars.

    Content is read directly from the configured LOCAL content-repo root
    (:class:`ego_server.content_config.TasksRepoConfig`) — never from
    SQLite blobs. The DB row supplies only identity metadata (``id``,
    ``version``, ``md_path``).

    ``writable`` is ``False`` with a concise ``read_only_reason`` when the
    repo is unconfigured / non-local / missing / unwritable, or when any
    resolved task/sidecar path escapes the canonical root via ``..`` or a
    symlink. When content cannot be read safely, the string fields are
    empty and only the DB identity metadata is returned.

    A missing optional ``.tests.py`` sidecar yields an empty string. A
    missing required ``.md`` returns 404; a missing required
    ``.solution.py`` returns 409 (task exists in DB but its solution
    sidecar is inconsistent).
    """
    row = db.execute(
        "SELECT id, task_id, version, md_path FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    md_path_str = row["md_path"] or ""
    base = TaskStudioDTO(
        task_id=row["task_id"],
        version=row["version"],
        md_path=md_path_str,
    )

    root_status = resolve_root(safe_config())
    if not root_status.ok or root_status.path is None:
        return base.model_copy(update={"writable": False, "read_only_reason": root_status.reason})
    root = root_status.path

    writable = True
    reason = ""
    if not is_writable(root):
        writable = False
        reason = "content repo root is not writable"

    # --- markdown (required) ---
    md = contained_path(root, md_path_str)
    if md is None:
        return base.model_copy(
            update={
                "writable": False,
                "read_only_reason": "task markdown path escapes content root",
            }
        )
    if not md.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task markdown not found in content repo",
        )
    markdown = md.read_text(encoding="utf-8")

    # --- solution sidecar (required) ---
    sol_rel = _sidecar_rel(md_path_str, ".solution.py")
    sol = contained_path(root, sol_rel)
    if sol is None:
        return base.model_copy(
            update={
                "markdown": markdown,
                "writable": False,
                "read_only_reason": "solution path escapes content root",
            }
        )
    if not sol.is_file():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="solution sidecar missing in content repo",
        )
    solution_py = sol.read_text(encoding="utf-8")

    # --- tests sidecar (optional) ---
    tests_rel = _sidecar_rel(md_path_str, ".tests.py")
    tests = contained_path(root, tests_rel)
    tests_py = ""
    if tests is None:
        writable = False
        reason = "tests path escapes content root"
    elif tests.is_file():
        tests_py = tests.read_text(encoding="utf-8")

    return base.model_copy(
        update={
            "markdown": markdown,
            "solution_py": solution_py,
            "tests_py": tests_py,
            "writable": writable,
            "read_only_reason": reason,
        }
    )


def _sidecar_rel(md_path_str: str, suffix: str) -> str:
    """Derive a sidecar path string from the task's ``md_path``.

    ``task_f1.md`` + ``.solution.py`` → ``task_f1.solution.py``. Preserves
    any relative directory component of ``md_path_str``.
    """
    return str(Path(md_path_str).with_suffix(suffix))


# === Task Studio validate (POST /admin/tasks/{task_id}/studio/validate) ===


_STRICT_SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def _is_strict_semver(v: str) -> bool:
    """True iff ``v`` is a clean ``MAJOR.MINOR.PATCH`` (no pre-release/build)."""
    return bool(_STRICT_SEMVER_RE.match(v))


def _semver_tuple(v: str) -> tuple[int, int, int] | None:
    """Parse ``'1.2.3'`` → ``(1, 2, 3)``. Returns ``None`` if not 3 int parts."""
    parts = v.split(".")
    if len(parts) != 3:
        return None
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def _semver_gt(a: str, b: str) -> bool:
    """True iff SemVer ``a`` > ``b`` (string fallback for non-SemVer values)."""
    ta = _semver_tuple(a)
    tb = _semver_tuple(b)
    if ta is None or tb is None:
        return a > b
    return ta > tb


@router.post(
    "/tasks/{task_id}/studio/validate",
    response_model=StudioValidateResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def validate_task_studio(
    task_id: str, body: StudioValidateRequest, db: DbDep
) -> StudioValidateResponse:
    """Validate a Task Studio candidate without modifying canonical files.

    Accepts the full candidate markdown (with YAML frontmatter), solution,
    and tests sidecars. Validation is entirely read-only with respect to the
    content repo — the candidate is parsed from a temporary isolated
    directory, so canonical files remain byte-identical.

    Failure modes:

    - **404** — task ``task_id`` not found in the DB.
    - **409** — content repo is unconfigured / non-local / missing / not
      writable; the DB-stored ``md_path`` escapes the canonical root via
      ``..`` or a symlink; ``expected_version`` does not match the current
      DB version (optimistic concurrency); or the project uses
      ``version_policy=declare``, content changed, and the candidate
      version is not strictly greater than the current version.
    - **422** — frontmatter is missing/malformed; frontmatter ``id`` does
      not match the DB task identity; candidate version is not valid
      strict SemVer; the candidate markdown + sidecars fail to parse
      through :func:`ego.parser.parse_task_file`; or the solution / tests
      do not compile as Python.
    """
    row = db.execute(
        "SELECT id, task_id, version, md_path, project_id FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # --- root + writability (409 on read-only / unconfigured) ---
    root_status = resolve_root(safe_config())
    if not root_status.ok or root_status.path is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"content repo is read-only: {root_status.reason}",
        )
    root = root_status.path
    if not is_writable(root):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="content repo root is not writable",
        )

    # --- canonical path containment (409 on traversal / symlink escape) ---
    md_path_str = row["md_path"] or ""
    md_canonical = contained_path(root, md_path_str)
    if md_canonical is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="task markdown path escapes content root",
        )

    # --- expected_version optimistic concurrency (409 on mismatch) ---
    current_version = row["version"]
    if body.expected_version != current_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"expected_version {body.expected_version!r} does not match "
                f"current version {current_version!r}"
            ),
        )

    # --- frontmatter parse + id match (422 on malformed / mismatch) ---
    from ego.catalog import parse_task_frontmatter

    try:
        fm, _body = parse_task_frontmatter(body.markdown)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"malformed frontmatter: {e}",
        )
    if fm is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="candidate markdown must include YAML frontmatter",
        )
    if fm.id != row["id"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"frontmatter id {fm.id!r} does not match task id {row['id']!r}",
        )

    # --- candidate version: strict SemVer (422 on invalid) ---
    candidate_version = fm.version
    if not _is_strict_semver(candidate_version):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"candidate version {candidate_version!r} is not valid strict "
                f"SemVer (expected MAJOR.MINOR.PATCH)"
            ),
        )

    # --- version_policy lookup (default 'declare' for legacy/no project) ---
    version_policy = "declare"
    project_id = row["project_id"]
    if project_id:
        prow = db.execute(
            "SELECT version_policy FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        if prow is not None:
            version_policy = prow["version_policy"]

    # --- content changed? (read canonical for comparison; no writes) ---
    canonical_md = md_canonical.read_text(encoding="utf-8") if md_canonical.is_file() else ""
    sol_canonical_p = contained_path(root, _sidecar_rel(md_path_str, ".solution.py"))
    canonical_sol = (
        sol_canonical_p.read_text(encoding="utf-8")
        if (sol_canonical_p is not None and sol_canonical_p.is_file())
        else ""
    )
    tests_canonical_p = contained_path(root, _sidecar_rel(md_path_str, ".tests.py"))
    canonical_tests = (
        tests_canonical_p.read_text(encoding="utf-8")
        if (tests_canonical_p is not None and tests_canonical_p.is_file())
        else ""
    )
    content_changed = (
        body.markdown != canonical_md
        or body.solution_py != canonical_sol
        or body.tests_py != canonical_tests
    )

    # --- version_policy=declare + changed content → must bump (409) ---
    if version_policy == "declare" and content_changed:
        if not _semver_gt(candidate_version, current_version):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"version_policy=declare requires candidate version > current "
                    f"({current_version}) when content changed, got {candidate_version}"
                ),
            )

    # --- parse through the existing parser using a temp isolated candidate (422) ---
    from ego.parser import parse_task_file

    md_name = Path(md_path_str).name
    sol_name = Path(md_path_str).with_suffix(".solution.py").name
    with tempfile.TemporaryDirectory(prefix="ego-studio-validate-") as tmp:
        tmp_dir = Path(tmp)
        (tmp_dir / md_name).write_text(body.markdown, encoding="utf-8")
        (tmp_dir / sol_name).write_text(body.solution_py, encoding="utf-8")
        if body.tests_py:
            tests_name = Path(md_path_str).with_suffix(".tests.py").name
            (tmp_dir / tests_name).write_text(body.tests_py, encoding="utf-8")
        try:
            parse_task_file(tmp_dir / md_name)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"candidate failed to parse: {e}",
            )

    # --- Python compile: solution (required) + tests (if nonempty) (422) ---
    try:
        compile(body.solution_py, "<candidate.solution.py>", "exec")
    except SyntaxError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"solution_py has a syntax error: {e}",
        )
    if body.tests_py:
        try:
            compile(body.tests_py, "<candidate.tests.py>", "exec")
        except SyntaxError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"tests_py has a syntax error: {e}",
            )

    return StudioValidateResponse(
        valid=True,
        task_id=row["task_id"],
        current_version=current_version,
        candidate_version=candidate_version,
        content_changed=content_changed,
        version_policy=version_policy,
    )


# === Helpers ===


def _resolve_path(path_str: str) -> Path:
    """Resolve a path that may be a ``file://`` URL or a bare local path.

    Handles Windows-style paths where a drive letter (``C:``) may appear
    in the URL. Accepts both ``file:///C:/path`` (triple slash, RFC) and
    ``file://C:/path`` (common but non-RFC) forms.
    """
    if path_str.startswith("file://"):
        from urllib.parse import urlparse
        import sys

        parsed = urlparse(path_str)
        # Reconstruct path: on Windows, urlparse may put 'C:' in netloc
        # for 'file://C:/path' (non-RFC form). Prefer netloc+path if so.
        if (
            parsed.netloc
            and sys.platform == "win32"
            and len(parsed.netloc) >= 2
            and parsed.netloc[1] == ":"
        ):
            p = parsed.netloc + parsed.path
        else:
            p = parsed.path
            # file:///C:/path → parsed.path = '/C:/path' → strip leading slash.
            if sys.platform == "win32" and len(p) >= 3 and p[0] == "/" and p[2] == ":":
                p = p[1:]
        return Path(p)
    return Path(path_str)


def _to_dto(result, *, repo_url: str) -> SyncResultDTO:
    """Convert :class:`ego_server.sync.SyncResult` to :class:`SyncResultDTO`."""
    return SyncResultDTO(
        log_id=result.log_id or 0,
        status=result.status,
        added=result.added,
        updated=result.updated,
        skipped=result.skipped,
        errors=result.errors,
        error_details=result.error_details_text,
        started_at=result.started_at,
        finished_at=result.finished_at,
        git_sha=result.git_sha,
        repo_url=repo_url,
    )
