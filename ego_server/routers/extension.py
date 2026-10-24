"""Extension distribution router — public ``latest`` + ``download`` (no auth).

A new student needs the VS Code extension *before* having an account, so
these two endpoints are deliberately unauthenticated (like ``/student`` and
the other static pages). They only expose the published package metadata:

- ``GET /extension/latest``   → version / sha256 / size / published_at /
  download_url (404 with a clear detail when nothing is published);
- ``GET /extension/download`` → the current ``cogito-<version>.vsix``.

Nothing outside :attr:`ego_server.config.Settings.extension_dir` is ever
served: ``file`` from ``latest.json`` must be a plain file name and the
resolved path must stay inside the directory.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ego_server import config
from ego_server.analytics import record_event
from ego_server.deps import DbDep
from ego_server.extension_dist import (
    DOWNLOAD_PATH,
    ExtensionPublishError,
    contained_file,
    extension_dir,
    read_latest,
)


router = APIRouter()

_NOTHING_PUBLISHED = "The VS Code extension is not published on this server"


class ExtensionLatestDTO(BaseModel):
    version: str
    sha256: str
    size: int
    published_at: str
    download_url: str
    notes: str | None = None
    mandatory: bool = False


def _directory() -> Path:
    """Read through the module so test reloads of the config are picked up."""
    return extension_dir(config.settings)


def _current_release():
    """Return the published release or raise the matching HTTP error."""
    directory = _directory()
    try:
        release = read_latest(directory)
    except ExtensionPublishError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"The published extension metadata is invalid: {exc}",
        ) from exc
    if release is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{_NOTHING_PUBLISHED} yet (latest.json not found).",
        )
    return release


def _current_release_file():
    """Return the published release and the contained path of its package."""
    release = _current_release()
    path = contained_file(_directory(), release.file)
    if path is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The published extension 'file' must be a plain file name inside "
            "EGO_EXTENSION_DIR",
        )
    return release, path


@router.get("/latest", response_model=ExtensionLatestDTO)
async def extension_latest(request: Request, db: DbDep) -> ExtensionLatestDTO:
    """Metadata of the newest published extension build."""
    release, _path = _current_release_file()
    installed_version = request.headers.get("x-cogito-extension-version", "")
    if installed_version.strip():
        record_event(db, request, "extension_active", installed_version)
    return ExtensionLatestDTO(
        version=release.version,
        sha256=release.sha256,
        size=release.size,
        published_at=release.published_at,
        download_url=DOWNLOAD_PATH,
        notes=release.notes,
        mandatory=release.mandatory,
    )


@router.get("/download", response_class=FileResponse)
async def extension_download(request: Request, db: DbDep) -> FileResponse:
    """Serve the current ``cogito-<version>.vsix`` (never cached)."""
    release, path = _current_release_file()
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The published extension file {release.file} is missing on the server",
        )
    record_event(db, request, "extension_download", release.version)
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=release.file,
        headers={"Cache-Control": "no-store"},
    )
