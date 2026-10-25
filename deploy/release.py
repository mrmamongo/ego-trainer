#!/usr/bin/env python3
"""Cogito release tool — the only supported way to put a release on the server.

Runs ON the production server (``31.130.149.12``, ``/opt/cogito``) with the
system ``python3`` and the standard library only. It generalises the ad-hoc
``release.py`` scripts of earlier releases (student-64fcff7,
content-f610d0b, release-6c2f86f, ...) into one committed, reusable flow:

1. lock — ``/opt/cogito/releases/.lock`` is created with ``O_EXCL``, so two
   releases can never interleave (that happened once and silently broke
   /panel and /ide).
2. precondition — the image the running container uses must equal
   ``--expect-current``; a parallel release that already switched the image
   is caught here instead of being overwritten.
3. candidate — a throwaway container of the NEW image runs against copies
   of the live database (SQLite backup API), the content tree and the
   ``data/extension`` directory, syncs tasks, then the generic checks run
   against it: /health, the pages, every /static asset referenced by them,
   unchanged student/progress/run/settings counters, unchanged 'stale'
   progress count and optional catalog counts (``--expect``).
4. backup — the live DB (backup API), ``.env``, the content dirs that will
   be replaced and (with ``--publish-vsix``) the current extension dir go to
   ``/opt/cogito/releases/<name>/backup``.
5. switch — place new content, sync tasks, switch ``COGITO_IMAGE`` in
   ``.env``, ``docker compose up -d --no-deps cogito-server``; if the new
   container does not become healthy, ``.env`` is restored and the previous
   image is brought back.
6. live checks — the same checks as on the candidate, now against
   ``127.0.0.1:18081``. Any failure rolls the release back (``.env`` and
   content from the backup), failure to roll back is reported loudly.
7. optional ``--publish-vsix`` — copy the package into
   ``/opt/cogito/incoming/<name>/`` (mounted read-only as
   ``/var/lib/ego/incoming``), run ``ego-server admin publish-extension``
   inside the container and check ``/extension/latest``.
8. publish — tag and push the running image as
   ``git.born-in-july.ru/mrmamongo/cogito:<name>`` (and ``:v<name>`` for the
   git release tag) so a rollback can pull it back.
9. cleanup — only the running image stays locally (other ``ego-trainer:``
   and registry tags are removed, image and builder caches pruned), root
   disk usage is printed, then ``DEPLOY OK``.

Configuration is CLI flags, optionally completed by a JSON file
(``--config release.json``). See ``deploy/README.md``.

Exit codes: 0 — DEPLOY OK; 1 — aborted (precondition/check/rollback);
2 — usage or config error; 3 — another release is running; 130 — interrupted.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path("/opt/cogito")
REGISTRY = "git.born-in-july.ru/mrmamongo/cogito"
LOCAL_IMAGE_PREFIX = "ego-trainer:"
COMPOSE_SERVICE = "cogito-server"
LIVE_CONTAINER = "cogito-cogito-server-1"
CANDIDATE_CONTAINER = "rel-candidate"
LIVE_PORT = 18081
CANDIDATE_PORT = 18099

DEFAULT_PAGES = ("/", "/panel", "/ide", "/student")
# Row counts that must never change during a release.
BASE_TABLES = ("students", "progress", "runs", "service_settings")
# CSS marker proving the student cabinet dark theme survived the build.
DARK_THEME_MARKER = '[data-theme="dark"]'
CANDIDATE_JWT_SECRET = "0123456789abcdef0123456789abcdef0123456789abcdef"
CONTAINER_UID_GID = "10001:10001"

EXIT_OK = 0
EXIT_ABORT = 1
EXIT_USAGE = 2
EXIT_LOCKED = 3
EXIT_INTERRUPTED = 130


class ReleaseError(Exception):
    """A release step failed; ``rolled_back`` says whether production is clean."""

    def __init__(self, message: str, rolled_back: bool = False):
        super().__init__(message)
        self.rolled_back = rolled_back


class ConfigError(ReleaseError):
    """Invalid CLI/JSON configuration (exit code 2)."""


class CheckFailed(ReleaseError):
    """A candidate or live check failed."""


class LockBusy(Exception):
    """The release lock is held by another process."""


class CommandFailed(Exception):
    """A subprocess returned a non-zero exit code."""


def _is_root() -> bool:
    """True when the tool runs as root (it then chowns placed files).

    The tool targets the prod server (Linux), but stays importable on other
    platforms so the pure helpers can be unit-tested anywhere.
    """
    return hasattr(os, "getuid") and os.getuid() == 0


def _hostname() -> str:
    try:
        return os.uname().nodename
    except AttributeError:  # not Linux
        return "localhost"


# ---------------------------------------------------------------------------
# Pure helpers (tested in tests/test_deploy_release.py)
# ---------------------------------------------------------------------------

_ASSET_TAG_RE = re.compile(
    r"<(?:script|link|img)\b[^>]*>\s*(?:</script\s*>)?", re.IGNORECASE
)
_ASSET_ATTR_RE = re.compile(
    r"""\b(?:src|href)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""", re.IGNORECASE
)


def extract_asset_refs(html: str, prefix: str = "/static/") -> list[str]:
    """Return unique same-origin asset paths referenced by ``html``.

    An asset reference is the ``src`` or ``href`` attribute of a ``<script>``,
    ``<link>`` or ``<img>`` element that points below ``prefix``. Query
    strings and fragments are dropped (the ``?v=1`` cache-buster is
    irrelevant for an existence check); template placeholders such as
    ``{{BRAND_LOGO_URL}}``, anchors and absolute URLs are ignored. The order
    of first appearance is preserved.
    """
    seen: dict[str, None] = {}
    for tag in _ASSET_TAG_RE.findall(html):
        for match in _ASSET_ATTR_RE.finditer(tag):
            ref = next(group for group in match.groups() if group is not None).strip()
            if not ref.startswith(prefix):
                continue
            path = re.split(r"[?#]", ref, maxsplit=1)[0]
            if len(path) <= len(prefix):
                continue
            seen.setdefault(path, None)
    return list(seen)


# The same SQL the earlier release scripts used. ``base`` counters go to the
# "must not change" comparison, ``sql`` counters are compared with --expect.
CATALOG_COUNTERS: dict[str, str] = {
    "start_tasks": "SELECT COUNT(*) FROM tasks WHERE project_id = 'python-start'",
    "start_folders": (
        "SELECT COUNT(DISTINCT folder_id) FROM tasks WHERE project_id = 'python-start'"
    ),
    "lessons": "SELECT COUNT(*) FROM lessons",
    "xla_tasks": "SELECT COUNT(*) FROM tasks WHERE project_id = 'xl-a' AND folder_id = 'xl_a'",
    "xla_v110": "SELECT COUNT(*) FROM tasks WHERE project_id = 'xl-a' AND version = '1.1.0'",
    "stale": "SELECT COUNT(*) FROM progress WHERE status = 'stale'",
}
# Names accepted in --expect beyond the catalogue counters.
EXPECT_ALIASES = (
    "<project>_tasks",
    "<project>_folders",
    *BASE_TABLES,
    *(f"base.{table}" for table in BASE_TABLES),
)


def _quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def check_sql(expect: dict[str, int] | None = None) -> dict[str, str]:
    """Build the counter name → SQL map used to read the database.

    ``base`` (students, progress, runs, service_settings) and ``stale`` are
    always read; they must not change during a release. Any other name in
    ``expect`` that is not a known counter is treated as a catalog project:
    ``<project>_tasks`` counts its tasks and ``<project>_folders`` its
    distinct folders. Unknown names raise :class:`ConfigError` so a typo in
    ``--expect`` cannot silently pass.
    """
    queries = dict(CATALOG_COUNTERS)
    for table in BASE_TABLES:
        queries[table] = f"SELECT COUNT(*) FROM {table}"
    for key, value in (expect or {}).items():
        if key in queries or key.startswith("base."):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ConfigError(f"--expect {key}: value must be a non-negative integer")
            continue
        if key.endswith("_tasks") and len(key) > len("_tasks"):
            project = key[: -len("_tasks")]
            queries[key] = (
                f"SELECT COUNT(*) FROM tasks WHERE project_id = {_quote_literal(project)}"
            )
        elif key.endswith("_folders") and len(key) > len("_folders"):
            project = key[: -len("_folders")]
            queries[key] = (
                "SELECT COUNT(DISTINCT folder_id) FROM tasks "
                f"WHERE project_id = {_quote_literal(project)}"
            )
        else:
            raise ConfigError(
                f"unknown --expect counter {key!r}; use "
                f"{', '.join(sorted(CATALOG_COUNTERS))} or <project>_tasks / <project>_folders"
            )
    return queries


def read_counts(db_path: Path | str, expect: dict[str, int] | None = None) -> dict:
    """Read the release counters from ``db_path`` (read-only connection).

    The connection is closed explicitly (``with sqlite3.connect`` only commits)
    so a report on a throwaway DB copy does not keep the file locked.
    """
    queries = check_sql(expect)
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        base = {
            table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in BASE_TABLES
        }
        values = {name: db.execute(sql).fetchone()[0] for name, sql in queries.items()}
    finally:
        db.close()
    return {"base": base, **values}


def compare_counts(
    after: dict,
    before: dict,
    expect: dict[str, int] | None = None,
    label: str = "check",
) -> list[str]:
    """Compare counters after a release step with the ones before it.

    Returns human-readable problems (an empty list means OK):

    - ``students``/``progress``/``runs``/``service_settings`` row counts must
      be unchanged — a release must not create or delete accounts, progress
      rows, run logs or settings;
    - the number of progress rows with status ``'stale'`` must be unchanged —
      a stale bump means the content sync lost or rewrote task identity;
    - counters present before must not change unless ``--expect`` pins them;
      a pinned counter must match its expected value (otherwise the content
      does not contain what the release is supposed to deliver);
    - a counter that vanished must match its expectation too (or is an
      error when it was never expected);
    - a counter that did not exist before may only appear when ``--expect``
      names it (first task of a brand-new project).
    """
    problems: list[str] = []
    before_all = dict(before or {})
    after_all = dict(after or {})
    expect = expect or {}
    before_base = before_all.pop("base", None) or {}
    after_base = after_all.pop("base", None) or {}
    for table in BASE_TABLES:
        old = before_base.get(table)
        new = after_base.get(table)
        if old != new:
            problems.append(f"{label}: {table} rows changed {old} -> {new}")
    for key, expected in expect.items():
        if key.startswith("base.") and key.split(".", 1)[1] in before_base:
            if before_base[key.split(".", 1)[1]] != expected:
                problems.append(f"{label}: expected {key}={expected}, before had "
                                f"{before_base[key.split('.', 1)[1]]}")
    for key in sorted(set(before_all) | set(after_all)):
        old = before_all.get(key)
        new = after_all.get(key)
        if key == "stale":
            if old != new:
                if new is None:
                    problems.append(f"{label}: progress rows with status 'stale' "
                                    f"disappeared (was {old})")
                elif old is None:
                    problems.append(f"{label}: progress rows with status 'stale' "
                                    f"appeared ({new})")
                else:
                    problems.append(
                        f"{label}: progress rows with status 'stale' changed {old} -> {new}"
                    )
            continue
        if key in expect:
            if new != expect[key]:
                problems.append(f"{label}: expected {key}={expect[key]}, got {new}")
            elif old is not None and new != old and new != expect[key]:
                problems.append(f"{label}: {key} changed {old} -> {new}, "
                                f"expected {expect[key]}")
            continue
        if new is None:
            problems.append(f"{label}: counter {key} disappeared (was {old})")
        elif old is None:
            problems.append(f"{label}: counter {key} appeared ({new}) without --expect")
        elif new != old:
            problems.append(f"{label}: {key} changed {old} -> {new}")
    for key, expected in expect.items():
        if key.startswith("base."):
            table = key.split(".", 1)[1]
            if after_base.get(table) != expected:
                problems.append(f"{label}: expected {key}={expected}, "
                                f"got {after_base.get(table)}")
    return problems


_ENV_IMAGE_RE = re.compile(r"^COGITO_IMAGE=.*$", re.MULTILINE)


def replace_env_image(env_text: str, image: str) -> str:
    """Return ``.env`` text with ``COGITO_IMAGE`` set to ``image``.

    The line is replaced literally; exactly one ``COGITO_IMAGE=`` line must
    exist (missing or duplicated key would make the switch ambiguous) and
    the new value must differ from the old one.
    """
    if not image or image.strip() != image or "\n" in image or "\r" in image:
        raise ConfigError(f"invalid image reference {image!r}")
    new_text, count = _ENV_IMAGE_RE.subn(lambda _m: f"COGITO_IMAGE={image}", env_text)
    if count != 1:
        raise ConfigError(
            f".env must contain exactly one COGITO_IMAGE line (found {count})"
        )
    return new_text


def env_image(env_text: str) -> str | None:
    """Return the ``COGITO_IMAGE`` value of ``.env`` text (``None`` if absent)."""
    match = re.search(r"^COGITO_IMAGE=(.*)$", env_text, re.MULTILINE)
    return match.group(1).strip() if match else None


_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}")
_PROJECT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
_IMAGE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/:@-]*")


def validate_name(name: str) -> str:
    """Release names become a directory below releases/ and a registry tag."""
    if not _NAME_RE.fullmatch(name or ""):
        raise ConfigError(
            f"release name {name!r} must match [A-Za-z0-9][A-Za-z0-9._-]* "
            "(it names releases/<name> and the registry tag)"
        )
    return name


def validate_image(ref: str) -> str:
    if not _IMAGE_RE.fullmatch(ref or ""):
        raise ConfigError(f"invalid image reference {ref!r}")
    return ref


def parse_expect(items: list[str] | None) -> dict[str, int]:
    """Parse ``--expect key=value`` items into ``{key: non-negative int}``."""
    result: dict[str, int] = {}
    for item in items or []:
        key, sep, value = item.partition("=")
        key = key.strip()
        value = value.strip()
        if not sep or not key or not re.fullmatch(r"\d+", value):
            raise ConfigError(f"--expect {item!r} must look like key=non-negative-integer")
        if key in result and result[key] != int(value):
            raise ConfigError(f"--expect {key} given twice with different values")
        result[key] = int(value)
    return result


def cleanup_targets(
    images: list[str],
    running: str,
    registry: str = REGISTRY,
    prefix: str = LOCAL_IMAGE_PREFIX,
) -> list[str]:
    """Image refs to remove locally after a release: keep only ``running``."""
    targets: set[str] = set()
    for ref in images:
        ref = ref.strip()
        if not ref or ref == running or "<none>" in ref:
            continue
        if ref.startswith(prefix) or ref.startswith(registry + ":"):
            targets.add(ref)
    return sorted(targets)


def format_disk(lines: list[str] | str) -> str:
    """Pick the root-filesystem row out of ``df -h /`` output."""
    rows = [line for line in (lines.splitlines() if isinstance(lines, str) else lines)
            if line.strip()]
    if not rows:
        return "unknown"
    return rows[-1]


# ---------------------------------------------------------------------------
# Side effects: Runner (subprocess) and fetch (HTTP), injectable for tests
# ---------------------------------------------------------------------------


def _subprocess_run(argv: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(argv, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


class Runner:
    """Runs commands through ``func`` (returns ``(code, stdout, stderr)``).

    Commands that only read state are passed with ``mutating=False`` and run
    even in dry-run mode (a plan is built from the real running image); in
    dry-run mode mutating commands are not executed but printed as
    ``[dry-run] ...`` and their output is ``read_empty``. Tests inject ``func``
    to replace docker entirely.
    """

    def __init__(
        self,
        func: Callable[[list[str]], tuple[int, str, str]] | None = None,
        dry_run: bool = False,
    ):
        self.func = func or _subprocess_run
        self.dry_run = dry_run

    def __call__(
        self,
        argv: list[str],
        check: bool = True,
        read_empty: str = "",
        mutating: bool = True,
    ) -> str:
        shown = " ".join(argv)
        if self.dry_run and mutating:
            print(f"  [dry-run] {shown}")
            return read_empty
        print(f"  $ {shown}")
        try:
            code, out, err = self.func(argv)
        except OSError as exc:
            raise CommandFailed(f"cannot run {shown}: {exc}") from exc
        out = (out or "").strip()
        if check and code != 0:
            raise CommandFailed(
                f"command failed ({code}): {shown}\n{out}\n{(err or '').strip()}"
            )
        return out


def http_fetch(port: int, path: str, tries: int = 1, delay: float = 1.0) -> tuple[int | None, bytes]:
    """GET ``http://127.0.0.1:<port><path>``, retrying connection errors."""
    url = f"http://127.0.0.1:{port}{path}"
    status: int | None = None
    for attempt in range(max(tries, 1)):
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            status, body = exc.code, exc.read()
            if attempt == max(tries, 1) - 1:
                return status, body
        except OSError:
            status = None
            if attempt == max(tries, 1) - 1:
                return None, b""
        time.sleep(delay)
    return status, b""


# ---------------------------------------------------------------------------
# Lock
# ---------------------------------------------------------------------------


def acquire_lock(lock_path: Path) -> int:
    """Create ``lock_path`` with ``O_EXCL``; returns the fd or raises LockBusy."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        try:
            holder = lock_path.read_text(encoding="utf-8").strip()
        except OSError:
            holder = "?"
        raise LockBusy(
            f"another release is running (lock {lock_path} says: {holder}). "
            "If that process is gone, remove the lock file and retry."
        ) from None
    os.write(
        fd,
        f"pid={os.getpid()} started={time.strftime('%Y-%m-%dT%H:%M:%S')} "
        f"host={_hostname()}\n".encode(),
    )
    os.fsync(fd)
    return fd


def release_lock(lock_path: Path, fd: int | None) -> None:
    """Always called in ``finally`` — a failed release must not keep the lock."""
    if fd is None:
        return
    try:
        os.close(fd)
    except OSError:
        pass
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class Config:
    name: str
    expect_current: str
    image: str | None = None
    content: dict[str, Path] = field(default_factory=dict)
    expect: dict[str, int] = field(default_factory=dict)
    publish_vsix: Path | None = None
    notes: str | None = None
    require_dark_theme: bool = True
    registry: str = REGISTRY
    root: Path = ROOT

    @property
    def new_image(self) -> str:
        return self.image or self.expect_current

    @property
    def release_dir(self) -> Path:
        return self.root / "releases" / self.name

    @property
    def backup_dir(self) -> Path:
        return self.release_dir / "backup"

    @property
    def lock_path(self) -> Path:
        return self.root / "releases" / ".lock"

    @property
    def env_path(self) -> Path:
        return self.root / ".env"

    @property
    def live_db(self) -> Path:
        return self.root / "data" / "ego.db"

    @property
    def extension_dir(self) -> Path:
        return self.root / "data" / "extension"

    @property
    def content_root(self) -> Path:
        return self.root / "content"

    def content_dest(self, project: str) -> Path:
        return self.content_root / "projects" / project

    def registry_image(self, tag: str | None = None) -> str:
        return f"{self.registry}:{tag or self.name}"

    def incoming_vsix(self) -> Path:
        """Host path of the package; ``incoming/<name>`` is mounted as /var/lib/ego/incoming."""
        return self.root / "incoming" / self.name / "cogito.vsix"

    def incoming_remote(self) -> Path:
        """The same package as seen inside the container."""
        return Path("/var/lib/ego/incoming") / self.name / "cogito.vsix"

    def summary(self) -> str:
        lines = [
            f"release name       : {self.name}",
            f"root               : {self.root}",
            f"running image must : {self.expect_current}",
        ]
        if self.image:
            lines.append(f"new image          : {self.image}")
        else:
            lines.append("new image          : (none — content/extension only)")
        if self.content:
            for project, src in sorted(self.content.items()):
                lines.append(f"content            : {project}: {src} -> {self.content_dest(project)}")
        else:
            lines.append("content            : (none)")
        if self.publish_vsix:
            lines.append(f"publish vsix       : {self.publish_vsix} -> {self.incoming_remote()}")
        lines.append(f"backup dir         : {self.backup_dir}")
        lines.append(f"registry tags      : {self.registry_image()}, {self.registry_image('v' + self.name)}")
        if self.expect:
            lines.append("expected counters  : "
                         + ", ".join(f"{k}={v}" for k, v in sorted(self.expect.items())))
        lines.append(f"pages checked      : {', '.join(DEFAULT_PAGES)}")
        lines.append("checks             : /health, pages, /static assets referenced by pages"
                     + (f", {DARK_THEME_MARKER} in /static/student.css"
                        if self.require_dark_theme else ""))
        lines.append(f"guarded counters   : {', '.join(BASE_TABLES)} (unchanged), "
                     "stale (unchanged), other catalogue counters (unchanged)")
        lines.append(f"lock file          : {self.lock_path}")
        return "\n".join(lines)


_CONFIG_KEYS = frozenset(
    {"name", "image", "content", "expect_current", "expect", "publish_vsix", "notes"}
)


def _load_json(config_path: Path) -> dict:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(f"config file {config_path} not found") from None
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config file {config_path} is not valid JSON: {exc}") from None
    if not isinstance(data, dict):
        raise ConfigError(f"config file {config_path} must contain a JSON object")
    unknown = sorted(set(data) - _CONFIG_KEYS)
    if unknown:
        raise ConfigError(f"config file {config_path}: unknown keys {unknown}")
    return data


def load_config(
    *,
    config_path: Path | None = None,
    name: str | None = None,
    image: str | None = None,
    content: list[str] | None = None,
    expect_current: str | None = None,
    expect: list[str] | None = None,
    publish_vsix: str | None = None,
    notes: str | None = None,
    no_dark_theme_check: bool = False,
    root: Path | str = ROOT,
) -> Config:
    """Merge the JSON config file with CLI values (CLI wins) and validate.

    JSON shape::

        {
          "name": "release-abc1234",
          "image": "ego-trainer:release-abc1234",
          "content": {"python-start": "/opt/cogito/incoming/release-abc1234/python-start"},
          "expect_current": "ego-trainer:release-61f3a2b",
          "expect": {"start_tasks": 239, "lessons": 71},
          "publish_vsix": "/opt/cogito/incoming/release-abc1234/cogito-0.2.0.vsix",
          "notes": "tuples and sets"
        }

    ``root`` is injectable so tests (and ``--dry-run`` elsewhere) can point
    the tool at a scratch directory; on the server it stays ``/opt/cogito``.
    """
    data: dict = _load_json(Path(config_path)) if config_path is not None else {}

    if name is not None:
        data["name"] = name
    if image is not None:
        data["image"] = image
    if content:
        merged = dict(data.get("content") or {})
        for item in content:
            project, sep, src = item.partition("=")
            if not sep or not project.strip() or not src.strip():
                raise ConfigError(f"--content {item!r} must look like PROJECT=DIR")
            merged[project.strip()] = src.strip()
        data["content"] = merged
    if expect_current is not None:
        data["expect_current"] = expect_current
    if expect:
        merged_expect = {str(k): v for k, v in (data.get("expect") or {}).items()}
        merged_expect.update(parse_expect(expect))
        data["expect"] = merged_expect
    if publish_vsix is not None:
        data["publish_vsix"] = publish_vsix
    if notes is not None:
        data["notes"] = notes

    raw_name = data.get("name")
    if not raw_name:
        raise ConfigError("a release name is required (--name or \"name\" in the JSON config)")
    release_name = validate_name(str(raw_name))

    raw_current = data.get("expect_current")
    if not raw_current:
        raise ConfigError(
            "--expect-current IMAGE is required: the running container image must match "
            "(this catches parallel releases)"
        )
    current = validate_image(str(raw_current))

    raw_image = data.get("image")
    new_image = validate_image(str(raw_image)) if raw_image else None

    raw_content = data.get("content") or {}
    if not isinstance(raw_content, dict):
        raise ConfigError("\"content\" must be an object {project: host dir}")
    projects: dict[str, Path] = {}
    for project, src in raw_content.items():
        project = str(project)
        if not _PROJECT_RE.fullmatch(project) or project in (".", ".."):
            raise ConfigError(f"invalid project name {project!r}")
        path = Path(str(src))
        if not path.is_dir():
            raise ConfigError(f"content dir for {project} does not exist: {path}")
        projects[project] = path

    raw_expect = data.get("expect") or {}
    if not isinstance(raw_expect, dict):
        raise ConfigError("\"expect\" must be an object {counter: integer}")
    for key, value in raw_expect.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ConfigError(f"\"expect\" value for {key} must be a non-negative integer")
    expect_map = {str(key): int(value) for key, value in raw_expect.items()}
    check_sql(expect_map)  # validates counter names

    vsix = data.get("publish_vsix")
    vsix_path = Path(str(vsix)) if vsix else None
    if vsix_path is not None and not vsix_path.is_file():
        raise ConfigError(f"--publish-vsix file not found: {vsix_path}")

    if new_image is None and not projects and vsix_path is None:
        raise ConfigError("nothing to release: pass --image, --content and/or --publish-vsix")

    raw_notes = data.get("notes")
    if raw_notes is not None and not isinstance(raw_notes, str):
        raise ConfigError("\"notes\" must be a string")

    return Config(
        name=release_name,
        expect_current=current,
        image=new_image,
        content=projects,
        expect=expect_map,
        publish_vsix=vsix_path,
        notes=raw_notes,
        require_dark_theme=not no_dark_theme_check,
        root=Path(root),
    )


# ---------------------------------------------------------------------------
# The release
# ---------------------------------------------------------------------------


class Release:
    def __init__(
        self,
        config: Config,
        run: Runner | None = None,
        fetch: Callable[..., tuple[int | None, bytes]] = http_fetch,
        getuid: Callable[[], int] | None = None,
        dry_run: bool = False,
    ):
        self.cfg = config
        self.run = run if run is not None else Runner(dry_run=dry_run)
        self.fetch = fetch
        self.getuid = getuid if getuid is not None else (lambda: 0 if _is_root() else 1)
        self.dry_run = dry_run
        self.old_env: str | None = None
        self.old_content: dict[str, Path | None] = {}
        self.before: dict = {}
        self.switched = False
        self.compose = [
            "docker", "compose", "--project-directory", str(config.root),
            "-f", str(config.root / "compose.yaml"),
        ]

    # -- small helpers ---------------------------------------------------
    def step(self, text: str) -> None:
        print(f"\n== {text}")

    def http(self, port: int, path: str, tries: int = 1) -> tuple[int | None, bytes]:
        if self.dry_run:
            return 200, b""
        return self.fetch(port, path, tries)

    def require(self, port: int, path: str, label: str, tries: int = 1) -> bytes:
        status, body = self.http(port, path, tries)
        if status != 200:
            raise CheckFailed(f"{label}: GET {path} -> {status}")
        return body

    def _copy_live_db(self, dest: Path) -> None:
        """Consistent copy of the live DB through the SQLite backup API.

        Both connections are closed explicitly: ``with sqlite3.connect`` only
        commits, and an open handle would keep the copy locked (and unremovable)
        on a non-POSIX host.
        """
        dest.parent.mkdir(parents=True, exist_ok=True)
        src = sqlite3.connect(self.cfg.live_db)
        try:
            dst = sqlite3.connect(dest)
            try:
                src.backup(dst)
            finally:
                dst.close()
        finally:
            src.close()

    def _chown_if_root(self, path: Path, recursive: bool = True) -> None:
        if self.getuid() != 0:
            return
        flag = "-R" if recursive else ""
        argv = [a for a in ("chown", flag, CONTAINER_UID_GID, str(path)) if a]
        self.run(argv, check=False)

    # -- steps -----------------------------------------------------------
    def preconditions(self) -> None:
        """Abort unless the server looks like prod and runs --expect-current."""
        self.step("preconditions")
        cfg = self.cfg
        for path in (cfg.env_path, cfg.live_db, cfg.content_root, cfg.root / "compose.yaml"):
            if not path.exists():
                raise ReleaseError(f"missing {path} — run this tool on the prod server")
        if not self.dry_run:
            running = self.running_image()
            if running != cfg.expect_current:
                raise ReleaseError(
                    f"running image is {running!r}, expected {cfg.expect_current!r}. "
                    "Another release may have switched it — re-check "
                    f"`docker inspect {LIVE_CONTAINER}` before retrying."
                )
            print(f"  running image {running} matches --expect-current")
        else:
            print(f"  plan: running-image guard --expect-current={cfg.expect_current}")
        env_text = cfg.env_path.read_text(encoding="utf-8")
        pinned = env_image(env_text)
        if pinned is None:
            raise ReleaseError("COGITO_IMAGE is missing from .env")
        print(f"  .env COGITO_IMAGE={pinned}")
        if cfg.image and not self.dry_run:
            if self.image_ref(cfg.image) is None:
                raise ReleaseError(
                    f"image {cfg.image} is not present locally; the caller must build or "
                    f"pull it first (e.g. docker pull {cfg.registry_image()})"
                )
            print(f"  image {cfg.image} is present")
        if self.old_env is None:
            self.old_env = env_text

    def running_image(self) -> str:
        """Image reference the live container runs (``Config.Image``)."""
        out = self.run(["docker", "inspect", LIVE_CONTAINER], mutating=False)
        try:
            image = json.loads(out)[0]["Config"]["Image"]
        except (ValueError, KeyError, IndexError, TypeError):
            raise ReleaseError(
                f"cannot read the image of {LIVE_CONTAINER} — is Compose running?"
            ) from None
        return image

    def is_ref(self, ref: str, argv: list[str]) -> tuple[str, str] | None:
        """``(id, ref)`` via ``docker inspect --format {{.Id}}``, ``None`` if absent.

        "No such image" from docker means absent; any other failure raises
        :class:`CommandFailed`.
        """
        try:
            out = self.run([*argv, "--format", "{{.Id}}"], mutating=False)
        except CommandFailed as exc:
            if "no such" in str(exc).lower():
                return None
            raise
        if not out:
            return None
        return out, ref

    def image_ref(self, ref: str) -> tuple[str, str] | None:
        """``(id, ref)`` of a local image, or ``None`` when it is not present."""
        return self.is_ref(ref, ["docker", "image", "inspect", ref])

    @property
    def source_image(self) -> str:
        """Image whose content the release ships (and that gets registry tags).

        With ``--image`` the caller supplies a locally built image (remember to
        ``docker tag`` it ``ego-trainer:<name>``) or a pulled registry image.
        Content-only releases keep tagging the running image under the new
        release name, as the earlier scripts did.
        """
        return self.cfg.image or self.cfg.expect_current

    def candidate(self) -> None:
        """Run the new image/content on copies of live data and check it."""
        cfg = self.cfg
        self.step(f"candidate: {self.source_image} on a copy of the live DB/content")
        cand = cfg.release_dir / "candidate"
        if self.dry_run:
            self._chown_if_root(cand)
            self.run(["docker", "rm", "-f", CANDIDATE_CONTAINER], check=False)
            self.run([
                "docker", "run", "-d", "--name", CANDIDATE_CONTAINER, "--init",
                "-p", f"127.0.0.1:{CANDIDATE_PORT}:8000",
                "-e", f"EGO_JWT_SECRET={CANDIDATE_JWT_SECRET}",
                "-e", "EGO_DB_PATH=/var/lib/ego/ego.db",
                "-e", "EGO_TASKS_REPO_URL=/content",
                "-v", f"{cand / 'data'}:/var/lib/ego",
                "-v", f"{cand / 'content'}:/content:ro",
                self.source_image,
            ])
            self.sync_tasks(CANDIDATE_CONTAINER)
            self.check_pages(CANDIDATE_PORT, "candidate")
            self.run(["docker", "rm", "-f", CANDIDATE_CONTAINER], check=False)
            return
        shutil.rmtree(cand, ignore_errors=True)
        (cand / "data").mkdir(parents=True)
        self._copy_live_db(cand / "data" / "ego.db")
        if cfg.extension_dir.exists():
            shutil.copytree(cfg.extension_dir, cand / "data" / "extension")
        shutil.copytree(cfg.content_root, cand / "content")
        for project, src in cfg.content.items():
            dst = cand / "content" / "projects" / project
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
        self._chown_if_root(cand)
        before = read_counts(cand / "data" / "ego.db", cfg.expect)
        self.run(["docker", "rm", "-f", CANDIDATE_CONTAINER], check=False)
        self.run([
            "docker", "run", "-d", "--name", CANDIDATE_CONTAINER, "--init",
            "-p", f"127.0.0.1:{CANDIDATE_PORT}:8000",
            "-e", f"EGO_JWT_SECRET={CANDIDATE_JWT_SECRET}",
            "-e", "EGO_DB_PATH=/var/lib/ego/ego.db",
            "-e", "EGO_TASKS_REPO_URL=/content",
            "-v", f"{cand / 'data'}:/var/lib/ego",
            "-v", f"{cand / 'content'}:/content:ro",
            self.source_image,
        ])
        self.require(CANDIDATE_PORT, "/health", "candidate", tries=60)
        try:
            self.sync_tasks(CANDIDATE_CONTAINER)
            self.check_pages(CANDIDATE_PORT, "candidate")
            after = read_counts(cand / "data" / "ego.db", cfg.expect)
            problems = compare_counts(after, before, cfg.expect, "candidate")
            if problems:
                raise CheckFailed("\n".join(problems))
            print(f"  candidate counters: {after}")
        finally:
            self.run(["docker", "rm", "-f", CANDIDATE_CONTAINER], check=False)
            self._remove(cand)
        print("  candidate OK")

    @staticmethod
    def _remove(path: Path) -> None:
        """Remove a throwaway directory; a failure is reported, not swallowed."""
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
        except OSError as exc:
            print(f"  warning: could not remove {path}: {exc}")

    def sync_tasks(self, container: str) -> None:
        out = self.run([
            "docker", "exec", container, "ego-server", "admin", "sync-tasks",
            "--from", "/content",
        ],
            read_empty="(sync skipped in dry run)",
        )
        print(f"  sync: {out.splitlines()[-1] if out else '(no output)'}")

    def check_pages(self, port: int, label: str) -> None:
        """/health already checked by the caller; check pages, assets, theme."""
        if self.dry_run:
            print(f"  {label}: would check {', '.join(DEFAULT_PAGES)}, their /static "
                  "assets" + (", dark theme" if self.cfg.require_dark_theme else ""))
            return
        refs: list[str] = []
        for page in DEFAULT_PAGES:
            body = self.require(port, page, label)
            for ref in extract_asset_refs(body.decode("utf-8", "replace")):
                if ref not in refs:
                    refs.append(ref)
        broken = []
        for ref in refs:
            status, _ = self.http(port, ref, tries=3)
            if status != 200:
                broken.append(f"{ref} -> {status}")
        if broken:
            raise CheckFailed(
                f"{label}: static assets referenced by pages are not served: "
                + ", ".join(broken)
            )
        if self.cfg.require_dark_theme:
            css = self.require(port, "/static/student.css", label, tries=3)
            if DARK_THEME_MARKER.encode() not in css:
                raise CheckFailed(
                    f"{label}: /static/student.css lost {DARK_THEME_MARKER} (dark theme)"
                )
        print(f"  {label}: pages OK, {len(refs)} static asset(s) OK"
              + (", dark theme OK" if self.cfg.require_dark_theme else ""))

    def backup(self) -> None:
        cfg = self.cfg
        self.step(f"backup -> {cfg.backup_dir}")
        if not self.dry_run:
            cfg.backup_dir.mkdir(parents=True, exist_ok=True)
            self._copy_live_db(cfg.backup_dir / "ego-pre-release.db")
            shutil.copy2(cfg.env_path, cfg.backup_dir / "env.bak")
            for project in cfg.content:
                dst = cfg.content_dest(project)
                self.old_content[project] = dst if dst.exists() else None
                if dst.exists():
                    shutil.copytree(dst, cfg.backup_dir / "content" / project)
            if cfg.publish_vsix and cfg.extension_dir.exists():
                shutil.copytree(
                    cfg.extension_dir, cfg.backup_dir / "extension", dirs_exist_ok=True
                )
            self.before = read_counts(cfg.live_db, cfg.expect)
            print(f"  before: {self.before}")
        else:
            print(f"  plan: DB (backup API), .env, content {sorted(cfg.content)} -> "
                  f"{cfg.backup_dir}")

    def place_content(self) -> None:
        for project, src in self.cfg.content.items():
            dst = self.cfg.content_dest(project)
            dst.parent.mkdir(parents=True, exist_ok=True)
            staging = dst.with_name(dst.name + ".new")
            shutil.rmtree(staging, ignore_errors=True)
            shutil.copytree(src, staging)
            shutil.rmtree(dst, ignore_errors=True)
            staging.rename(dst)
            self._chown_if_root(dst)
            print(f"  placed {project} -> {dst}")

    def switch_image(self) -> None:
        """Rewrite COGITO_IMAGE and recreate the container; raise if unhealthy."""
        cfg = self.cfg
        assert self.old_env is not None
        new_env = replace_env_image(self.old_env, cfg.new_image)
        tmp = cfg.env_path.with_name(".env.release-tmp")
        tmp.write_text(new_env, encoding="utf-8")
        shutil.copymode(cfg.env_path, tmp)
        tmp.replace(cfg.env_path)
        self.run([*self.compose, "up", "-d", "--no-deps", COMPOSE_SERVICE])
        status, _ = self.http(LIVE_PORT, "/health", tries=60)
        if status != 200:
            raise ReleaseError(f"new container is unhealthy: /health -> {status}")
        print(f"  switched to {cfg.new_image}")

    def publish_vsix(self) -> None:
        cfg = self.cfg
        assert cfg.publish_vsix is not None
        self.step(f"publish extension {cfg.publish_vsix.name}")
        dest = cfg.incoming_vsix()
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cfg.publish_vsix, dest)
        argv = [
            "docker", "exec", LIVE_CONTAINER, "ego-server", "admin",
            "publish-extension", "--vsix", str(cfg.incoming_remote()),
        ]
        if cfg.notes:
            argv += ["--notes", cfg.notes]
        print(f"  {self.run(argv, read_empty='(publish skipped in dry run)')}")
        body = self.require(LIVE_PORT, "/extension/latest", "live", tries=5)
        try:
            payload = json.loads(body.decode("utf-8"))
        except ValueError:
            raise CheckFailed("live: /extension/latest is not JSON") from None
        print(f"  /extension/latest OK: version {payload.get('version')}")

    def publish_image(self) -> None:
        cfg = self.cfg
        self.step("registry")
        for tag in (cfg.name, "v" + cfg.name):
            ref = cfg.registry_image(tag)
            self.run(["docker", "tag", self.source_image, ref])
            self.run(["docker", "push", "-q", ref])
            print(f"  {'would push' if self.dry_run else 'pushed'} {ref}")

    def cleanup(self) -> None:
        cfg = self.cfg
        self.step("cleanup: keep only the running image")
        images = self.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            check=False,
            mutating=False,
        )
        for ref in cleanup_targets(images.splitlines(), self.source_image, cfg.registry):
            self.run(["docker", "rmi", ref], check=False)
        self.run(["docker", "image", "prune", "-f"], check=False)
        self.run(["docker", "builder", "prune", "-f"], check=False)
        print(f"  disk: {format_disk(self.run(['df', '-h', str(cfg.root)], read_empty=''))}")

    def rollback(self) -> bool:
        """Restore .env and content, bring the previous image back. True = clean."""
        cfg = self.cfg
        print("\n!! rolling back")
        try:
            if self.old_env is not None:
                cfg.env_path.write_text(self.old_env, encoding="utf-8")
            for project, old in self.old_content.items():
                dst = cfg.content_dest(project)
                if old is None:
                    shutil.rmtree(dst, ignore_errors=True)
                    continue
                staging = dst.with_name(dst.name + ".rollback")
                shutil.rmtree(staging, ignore_errors=True)
                shutil.copytree(cfg.backup_dir / "content" / project, staging)
                shutil.rmtree(dst, ignore_errors=True)
                staging.rename(dst)
                self._chown_if_root(dst)
            self.run([*self.compose, "up", "-d", "--no-deps", COMPOSE_SERVICE])
            status, _ = self.http(LIVE_PORT, "/health", tries=45)
            if cfg.content:
                self.sync_tasks(LIVE_CONTAINER)
            if status != 200:
                print(f"!! after rollback /health is {status}")
                return False
            print("  rollback: previous image and content are live again")
            return True
        except Exception as exc:  # noqa: BLE001 — rollback must report, not crash
            print(f"!! rollback failed: {exc}")
            return False

    # -- orchestration ---------------------------------------------------
    def execute(self) -> None:
        cfg = self.cfg
        self.preconditions()
        if cfg.image or cfg.content:
            self.candidate()
        self.backup()
        self.switched = True
        try:
            if cfg.content:
                self.step("switch content")
                self.place_content()
                self.sync_tasks(LIVE_CONTAINER)
            if cfg.image:
                self.step(f"switch image -> {cfg.image}")
                self.switch_image()
            self.step("live checks")
            self.require(LIVE_PORT, "/health", "live", tries=30)
            self.check_pages(LIVE_PORT, "live")
            after = read_counts(cfg.live_db, cfg.expect)
            print(f"  after: {after}")
            problems = compare_counts(after, self.before, cfg.expect, "live")
            if problems:
                raise CheckFailed("\n".join(problems))
            if cfg.publish_vsix:
                self.publish_vsix()
        except Exception as exc:
            rolled_back = self.rollback()
            message = str(exc) or exc.__class__.__name__
            tail = (
                "ROLLED BACK: production is on the previous state"
                if rolled_back
                else f"ROLLBACK INCOMPLETE — restore manually from {cfg.backup_dir}"
            )
            raise ReleaseError(f"release failed: {message}\n{tail}", rolled_back) from exc
        self.switched = False
        self.publish_image()

    def plan(self) -> None:
        """Dry run: print what would happen; no docker, no file writes."""
        self.preconditions()
        if self.cfg.image or self.cfg.content:
            self.candidate()
        self.backup()
        if self.cfg.content:
            self.step("switch content")
            print(f"  would place {', '.join(sorted(self.cfg.content))}")
            self.sync_tasks(LIVE_CONTAINER)
        if self.cfg.image:
            self.step(f"switch image -> {self.cfg.image}")
            new_env = replace_env_image(self.old_env or "", self.cfg.image)
            print(f"  .env: COGITO_IMAGE={env_image(new_env)}")
            self.run([*self.compose, "up", "-d", "--no-deps", COMPOSE_SERVICE])
        else:
            print(f"  image unchanged: {self.cfg.expect_current}")
        self.step("live checks")
        print(f"  would check 127.0.0.1:{LIVE_PORT}: /health, "
              f"{', '.join(DEFAULT_PAGES)}, their /static assets, counters")
        if self.cfg.publish_vsix:
            self.publish_vsix()
        self.publish_image()
        self.cleanup()


def run_release(
    config: Config,
    *,
    run: Runner | None = None,
    fetch: Callable[..., tuple[int | None, bytes]] = http_fetch,
    getuid: Callable[[], int] | None = None,
    dry_run: bool = False,
) -> int:
    """Run (or plan) a release. Returns the process exit code."""
    cfg = config
    if dry_run:
        print(f"DRY RUN — no docker commands, no file changes\n\n{cfg.summary()}\n")
        try:
            Release(cfg, run=run, fetch=fetch, getuid=getuid, dry_run=True).plan()
        except ReleaseError as exc:
            print(f"\nABORT: {exc}", file=sys.stderr)
            return EXIT_ABORT
        except CommandFailed as exc:
            print(f"\nABORT: {exc}", file=sys.stderr)
            return EXIT_ABORT
        print("\nDRY RUN OK — plan above; nothing was changed")
        return EXIT_OK

    try:
        lock_fd = acquire_lock(cfg.lock_path)
    except LockBusy as exc:
        print(f"ABORT: {exc}", file=sys.stderr)
        return EXIT_LOCKED
    except OSError as exc:
        print(f"ABORT: cannot create {cfg.lock_path}: {exc}", file=sys.stderr)
        return EXIT_ABORT
    release = Release(cfg, run=run, fetch=fetch, getuid=getuid)
    try:
        cfg.release_dir.mkdir(parents=True, exist_ok=True)
        release.execute()
        release.cleanup()
        print("\nDEPLOY OK")
        return EXIT_OK
    except ReleaseError as exc:
        print(f"\nABORT: {exc}", file=sys.stderr)
        return EXIT_ABORT
    except CommandFailed as exc:
        print(f"\nABORT: {exc}", file=sys.stderr)
        return EXIT_ABORT
    finally:
        release_lock(cfg.lock_path, lock_fd)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deploy/release.py",
        description=(
            "Cogito release tool for the prod server (/opt/cogito): lock, "
            "--expect-current guard, candidate on a copy of the live DB, "
            "backup, switch, live checks, rollback on failure, registry push, "
            "DEPLOY OK."
        ),
        epilog=(
            "examples:\n"
            "  deploy/release.py --config release.json\n"
            "  deploy/release.py --name release-abc1234 --image ego-trainer:release-abc1234 \\\n"
            "      --expect-current ego-trainer:61f3a2b \\\n"
            "      --expect start_tasks=239 --expect lessons=71\n"
            "  deploy/release.py --name content-f610d0b \\\n"
            "      --content python-start=/opt/cogito/incoming/content-f610d0b/python-start \\\n"
            "      --expect-current ego-trainer:release-8bc6212 --dry-run\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", type=Path, help="JSON config file (CLI flags win)")
    parser.add_argument("--name", help="release name: releases/<name> and registry tag")
    parser.add_argument(
        "--image",
        metavar="REF",
        help="image to run, e.g. git.born-in-july.ru/mrmamongo/cogito:<tag> or a locally built tag",
    )
    parser.add_argument(
        "--content",
        action="append",
        default=[],
        metavar="PROJECT=DIR",
        help="host dir placed into /opt/cogito/content/projects/PROJECT (repeatable)",
    )
    parser.add_argument(
        "--expect-current",
        metavar="IMAGE",
        help="image the running container must use now; abort otherwise",
    )
    parser.add_argument(
        "--expect",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="expected catalog counter, e.g. start_tasks=239 (repeatable)",
    )
    parser.add_argument(
        "--publish-vsix",
        metavar="FILE",
        help="publish this .vsix via 'ego-server admin publish-extension'",
    )
    parser.add_argument("--notes", help="release notes for --publish-vsix")
    parser.add_argument(
        "--no-dark-theme-check",
        action="store_true",
        help='skip the [data-theme="dark"] assertion on /static/student.css',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the config and the plan; no docker commands, no file changes",
    )
    return parser


def main(
    argv: list[str] | None = None,
    *,
    run: Runner | None = None,
    fetch: Callable[..., tuple[int | None, bytes]] = http_fetch,
    getuid: Callable[[], int] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = load_config(
            config_path=args.config,
            name=args.name,
            image=args.image,
            content=args.content,
            expect_current=args.expect_current,
            expect=args.expect,
            publish_vsix=args.publish_vsix,
            notes=args.notes,
            no_dark_theme_check=args.no_dark_theme_check,
        )
    except ConfigError as exc:
        parser.error(str(exc))  # argparse prints usage and exits with 2
        raise AssertionError("unreachable") from None
    try:
        return run_release(
            config, run=run, fetch=fetch, getuid=getuid, dry_run=args.dry_run
        )
    except KeyboardInterrupt:
        print("\nABORT: interrupted", file=sys.stderr)
        return EXIT_INTERRUPTED


if __name__ == "__main__":
    sys.exit(main())
