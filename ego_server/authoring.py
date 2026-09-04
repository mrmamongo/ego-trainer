"""Authoring path-safety helpers for Task Studio (read slice).

Centralises all filesystem path resolution + containment checks so the
admin router stays thin and the security rules are testable in isolation.

Rules (per the Task Studio read spec):
- Content is read ONLY from the configured local :class:`TasksRepoConfig`
  root — never from SQLite blobs and never from an unrelated location.
- Never follow paths outside the canonical root, whether via ``..``
  segments or symlinks. A candidate path is "contained" iff its real
  (resolved) filesystem path is equal to or strictly under the root's
  real path.
- When the repo is unconfigured / non-local / missing / unwritable, or a
  resolved path escapes the root, callers return metadata (and content
  only when safely readable) with ``writable=False`` and a concise
  reason rather than raising.

This module is deliberately free of FastAPI/HTTP concerns — it returns
plain dataclasses / ``Path | None`` so it can be unit-tested directly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from ego_server.content_config import TasksRepoConfig


@dataclass(frozen=True)
class RootStatus:
    """Outcome of resolving the configured content-repo root.

    ``ok`` is ``True`` only when a local, existing directory root was
    resolved. Otherwise ``path`` is ``None`` and ``reason`` carries a
    concise human-readable explanation.
    """

    ok: bool
    path: Path | None
    reason: str


def resolve_root(config: TasksRepoConfig) -> RootStatus:
    """Resolve and validate the configured local content-repo root.

    Returns :class:`RootStatus` with ``ok=True`` only for a local
    ``file://`` / bare-path URL that points to an existing directory.
    """
    if not config.url:
        return RootStatus(False, None, "content repo URL is not configured")

    # TasksRepoConfig rejects non-file URLs at validation time; if a
    # caller built one directly (or env reload produced an invalid
    # value), surface it as a read-only reason rather than raising.
    try:
        raw = config.url
    except Exception:  # pragma: no cover - defensive
        return RootStatus(False, None, "content repo URL is invalid")

    if "://" in raw and not raw.startswith("file://"):
        return RootStatus(False, None, "content repo URL is not local (file:// required)")

    try:
        root = config.resolved_local_path
    except Exception as e:  # noqa: BLE001 - any resolution failure → read-only
        return RootStatus(False, None, f"content repo root unresolvable: {e}")

    if not root.exists():
        return RootStatus(False, None, f"content repo root not found: {root}")
    if not root.is_dir():
        return RootStatus(False, None, f"content repo root is not a directory: {root}")

    return RootStatus(True, root.resolve(), "")


def contained_path(root: Path, rel: str) -> Path | None:
    """Resolve ``rel`` against ``root`` and verify it stays within root.

    ``rel`` may be absolute (e.g. as stored by sync) or relative. The
    candidate is resolved with symlinks followed, then checked for
    containment under ``root`` (also resolved). Returns the resolved
    ``Path`` when contained, or ``None`` when the path escapes the root
    via ``..`` or a symlink. Existence of the target is NOT required —
    callers decide how to handle a missing file.
    """
    if rel is None or rel == "":
        return None
    candidate = Path(rel)
    if not candidate.is_absolute():
        candidate = root / candidate

    try:
        resolved = candidate.resolve(strict=False)
        root_resolved = root.resolve(strict=False)
    except (OSError, RuntimeError):
        return None

    if _is_within(resolved, root_resolved):
        return resolved
    return None


def _is_within(path: Path, base: Path) -> bool:
    """True iff ``path`` equals or is strictly under ``base`` (both resolved)."""
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def is_writable(path: Path) -> bool:
    """Best-effort writability probe for a directory.

    Uses :func:`os.access` with ``W_OK``. On platforms that do not honour
    POSIX mode bits (Windows), this may report ``True`` even for a
    read-only-marked directory; callers/tests should treat a ``False``
    here as authoritative and a ``True`` as non-definitive.
    """
    try:
        return os.access(path, os.W_OK)
    except OSError:
        return False


def safe_config() -> TasksRepoConfig:
    """Build a :class:`TasksRepoConfig` from the env-loaded settings.

    Returns a config with an empty ``url`` if the env value is invalid
    (e.g. a non-local URL in PR 1), so the caller can surface a read-only
    reason via :func:`resolve_root` instead of crashing.
    """
    from ego_server.content_config import content_settings

    try:
        return content_settings.to_config()
    except ValidationError:
        return TasksRepoConfig(url="")
