"""VS Code extension distribution — ``latest.json`` + published ``.vsix`` files.

The server hosts the Cogito extension so a new student can install it before
having any account: ``GET /extension/latest`` and ``GET /extension/download``
are public (no JWT). The published state lives on disk in
:attr:`ego_server.config.Settings.extension_dir`:

- ``latest.json`` — ``{"version", "sha256", "file", "size", "published_at",
  "notes"?, "mandatory"?}`` written atomically by the CLI;
- ``cogito-<version>.vsix`` — the uploadable extension package.

``file`` is always a plain file name inside the directory: every read is
resolved and checked for containment so a hand-edited ``latest.json`` can
never make the server serve an arbitrary path.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

LATEST_FILE = "latest.json"

#: API download path (also advertised as ``download_url``).
DOWNLOAD_PATH = "/extension/download"

#: VS Code Marketplace / semver release version: ``MAJOR.MINOR.PATCH[-pre][+build]``.
VERSION_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)

#: A plain file name: no separators, no drive/UNC prefixes, no traversal.
_SAFE_FILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")

_READ_CHUNK = 1024 * 1024


class ExtensionPublishError(ValueError):
    """Raised when a ``.vsix`` cannot be published (bad file, stale version)."""


@dataclass(frozen=True)
class ReleaseInfo:
    """Content of ``latest.json`` as served by ``GET /extension/latest``."""

    version: str
    sha256: str
    file: str
    size: int
    published_at: str
    notes: str | None = None
    mandatory: bool = False
    extra: dict = field(default_factory=dict, compare=False)

    def to_json(self) -> dict:
        data: dict = {
            "version": self.version,
            "sha256": self.sha256,
            "file": self.file,
            "size": self.size,
            "published_at": self.published_at,
        }
        if self.notes:
            data["notes"] = self.notes
        if self.mandatory:
            data["mandatory"] = True
        # Unknown future keys must not block a known-good release.
        for key, value in self.extra.items():
            data.setdefault(key, value)
        return data


# === SemVer ===


def parse_version(version: str) -> tuple[int, int, int, tuple] | None:
    """Parse a SemVer release version into a sortable key (``None`` if invalid).

    Build metadata (``+build``) is ignored per the SemVer spec.
    """
    match = VERSION_RE.match(version.strip()) if isinstance(version, str) else None
    if match is None:
        return None
    major, minor, patch, pre, _build = match.groups()
    core = (int(major), int(minor), int(patch))
    if pre is None:
        return (*core, (1, ()))
    # A pre-release sorts before its release; identifiers are compared
    # numerically when numeric, then lexically, and a shorter set sorts first.
    identifiers = tuple(
        (0, int(part), "") if part.isdigit() else (1, 0, part) for part in pre.split(".")
    )
    return (*core, (0, identifiers))


def is_newer(candidate: str, current: str | None) -> bool:
    """True when ``candidate`` is a valid version newer than ``current``.

    No published release means anything valid is acceptable.
    """
    parsed = parse_version(candidate)
    if parsed is None:
        return False
    if current is None:
        return True
    existing = parse_version(current)
    return existing is None or parsed > existing


# === Paths ===


def extension_dir(settings) -> Path:
    """Directory holding ``latest.json`` and the published ``.vsix`` files."""
    configured = getattr(settings, "extension_dir", None)
    if configured:
        return Path(configured)
    # Default: ``extension`` next to the DB (``EGO_DB_PATH`` parent).
    return Path(settings.db_path).parent / "extension"


def is_plain_file_name(name: object) -> bool:
    """True for a bare file name like ``cogito-0.2.0.vsix`` (never a path)."""
    if not isinstance(name, str) or not name or len(name) > 255:
        return False
    if not _SAFE_FILE_RE.match(name):
        return False
    if "/" in name or "\\" in name or ":" in name or ".." in name:
        return False
    return name not in {".", "..", LATEST_FILE}


def vsix_file_name(version: str) -> str:
    """Published file name for a release version."""
    return f"cogito-{version}.vsix"


def contained_file(directory: Path, name: object) -> Path | None:
    """Resolve ``name`` inside ``directory``; ``None`` if it escapes it.

    Rejects anything that is not a plain file name (separators, ``..``,
    absolute/UNC/Windows drive prefixes) and symlinks pointing outside.
    Existence is not checked here.
    """
    if not is_plain_file_name(name):
        return None
    assert isinstance(name, str)
    try:
        root = Path(directory).resolve(strict=False)
        candidate = (root / name).resolve(strict=False)
    except (OSError, RuntimeError):
        return None
    if candidate == root or candidate.parent != root:
        return None
    return candidate


# === Reading the published state ===


def read_latest(directory: Path) -> ReleaseInfo | None:
    """Read ``latest.json``; ``None`` when nothing is published.

    Raises :class:`ExtensionPublishError` for an unreadable/invalid file so
    the endpoint can answer with a clear message instead of a 500.
    """
    path = Path(directory) / LATEST_FILE
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise ExtensionPublishError(f"cannot read {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ExtensionPublishError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ExtensionPublishError(f"{path} must contain a JSON object")

    version = data.get("version")
    sha256 = data.get("sha256")
    file_name = data.get("file")
    size = data.get("size")
    published_at = data.get("published_at")
    if not isinstance(version, str) or parse_version(version) is None:
        raise ExtensionPublishError(f"{path}: invalid 'version'")
    if not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise ExtensionPublishError(f"{path}: invalid 'sha256'")
    if not isinstance(file_name, str) or not is_plain_file_name(file_name):
        raise ExtensionPublishError(f"{path}: 'file' must be a plain file name")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ExtensionPublishError(f"{path}: invalid 'size'")
    if not isinstance(published_at, str) or not published_at:
        raise ExtensionPublishError(f"{path}: invalid 'published_at'")

    known = {"version", "sha256", "file", "size", "published_at", "notes", "mandatory"}
    notes = data.get("notes")
    return ReleaseInfo(
        version=version,
        sha256=sha256,
        file=file_name,
        size=size,
        published_at=published_at,
        notes=notes if isinstance(notes, str) and notes.strip() else None,
        mandatory=data.get("mandatory") is True,
        extra={k: v for k, v in data.items() if k not in known},
    )


# === Hashing ===


def sha256_file(path: Path) -> tuple[str, int]:
    """Return ``(hex sha256, size in bytes)`` of ``path``."""
    digest = hashlib.sha256()
    size = 0
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_READ_CHUNK), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


# === Publishing ===

_PACKAGE_JSON = "extension/package.json"


def read_vsix_version(vsix_path: Path) -> str:
    """Read the extension version from ``extension/package.json`` inside a vsix.

    Raises :class:`ExtensionPublishError` when the file is not a zip, has no
    ``package.json``, or carries an invalid version.
    """
    path = Path(vsix_path)
    if not path.is_file():
        raise ExtensionPublishError(f"vsix not found: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            entry = _PACKAGE_JSON if _PACKAGE_JSON in names else next(
                (n for n in names if n.endswith("/package.json") and n.count("/") == 1),
                None,
            )
            if entry is None:
                raise ExtensionPublishError(f"{path}: no extension/package.json inside the vsix")
            if archive.getinfo(entry).file_size > 1024 * 1024:
                raise ExtensionPublishError(f"{path}: {entry} is too large")
            manifest = json.loads(archive.read(entry).decode("utf-8"))
    except zipfile.BadZipFile as exc:
        raise ExtensionPublishError(f"{path}: not a valid .vsix (zip) file") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExtensionPublishError(f"{path}: cannot read {entry}: {exc}") from exc
    version = manifest.get("version") if isinstance(manifest, dict) else None
    if not isinstance(version, str) or parse_version(version) is None:
        raise ExtensionPublishError(f"{path}: invalid extension version {version!r}")
    return version.strip()


def _atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


@dataclass(frozen=True)
class PublishResult:
    release: ReleaseInfo
    path: Path
    previous_version: str | None

    def summary(self) -> str:
        """One-line CLI summary."""
        previous = self.previous_version or "—"
        return (
            f"Published {self.release.version} (was {previous}): {self.path} "
            f"{self.release.size} bytes, sha256 {self.release.sha256}"
        )


def publish_vsix(
    vsix_path: Path,
    directory: Path,
    *,
    force: bool = False,
    notes: str | None = None,
    mandatory: bool = False,
    now: datetime | None = None,
) -> PublishResult:
    """Copy ``vsix_path`` into ``directory`` and atomically update ``latest.json``.

    Refuses (raises :class:`ExtensionPublishError`) when the version inside the
    vsix is not newer than the currently published one, unless ``force``.
    """
    source = Path(vsix_path)
    version = read_vsix_version(source)
    directory = Path(directory)
    recent = read_latest(directory)

    if recent is not None and not force and not is_newer(version, recent.version):
        raise ExtensionPublishError(
            f"version {version} is not newer than the published {recent.version}; "
            f"bump the extension version or pass --force"
        )
    if recent is not None and recent.version == version and not force:
        raise ExtensionPublishError(f"version {version} is already published")

    sha256, size = sha256_file(source)
    file_name = vsix_file_name(version)
    directory.mkdir(parents=True, exist_ok=True)
    target = contained_file(directory, file_name)
    if target is None:  # pragma: no cover — generated names are always plain
        raise ExtensionPublishError(f"refusing unsafe target name: {file_name}")

    fd, tmp_name = tempfile.mkstemp(prefix=f".{file_name}.", suffix=".tmp", dir=directory)
    try:
        with open(source, "rb") as src, os.fdopen(fd, "wb") as dst:
            for chunk in iter(lambda: src.read(_READ_CHUNK), b""):
                dst.write(chunk)
            dst.flush()
            os.fsync(dst.fileno())
        os.replace(tmp_name, target)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise

    published_at = (now or datetime.now(UTC)).isoformat()
    release = ReleaseInfo(
        version=version,
        sha256=sha256,
        file=file_name,
        size=size,
        published_at=published_at,
        notes=(notes.strip() or None) if isinstance(notes, str) else None,
        mandatory=bool(mandatory),
    )
    _atomic_write_json(directory / LATEST_FILE, release.to_json())
    return PublishResult(
        release=release,
        path=target,
        previous_version=recent.version if recent is not None else None,
    )
