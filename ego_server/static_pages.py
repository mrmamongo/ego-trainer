"""Serve the static HTML shells with a content-hash cache-buster.

``admin.html`` and ``ide.html`` reference the built admin-ui assets under
``/static/admin/`` with a ``?v={{STATIC_ASSET_VERSION}}`` query. The placeholder
is replaced on every request with a version computed once at startup from the
content of the referenced asset files, so a rebuilt bundle never pairs with a
stale cached copy. The version is per file (not one flag for the whole build),
so rebuilding only the IDE still refreshes ``ide.js``.

The HTML itself stays ``Cache-Control: no-store``. Assets are served by
``StaticFiles``; their ``?v=`` query is part of the cache key, which is what
makes the busting effective.

Run ``python -m ego_server.static_pages`` to print the current build id.
"""

from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

from fastapi.responses import HTMLResponse

STATIC_DIR = Path(__file__).parent / "static"

# Built admin-ui outputs (paths relative to static/); see admin-ui/build.mjs.
_ASSET_FILES = (
    "admin/workers/editor.worker.js",
    "admin/monaco.LICENSE.txt",
    "admin/shadcn.LICENSE.txt",
    "admin/bundle.css",
    "admin/bundle.js",
    "admin/theme.css",
    "admin/ide.css",
    "admin/ide.js",
)
_VERSION_PLACEHOLDER = "{{STATIC_ASSET_VERSION}}"

# (src|href)="..." or url(...) values pointing at a local static asset.
_HTML_ASSET_REFERENCE = re.compile(
    r"""((?:src|href)\s*=\s*["']|url\(\s*["']?)(/[^"'\s)]+)""",
    re.IGNORECASE,
)


def _fingerprint(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(data).hexdigest()[:16]


def asset_version_map(static_dir: Path | None = None) -> dict[str, str]:
    """Map ``/static/<asset>`` URLs present on disk to their content hashes."""
    root = static_dir or STATIC_DIR
    versions: dict[str, str] = {}
    for name in _ASSET_FILES:
        digest = _fingerprint(root / name)
        if digest:
            versions["/static/" + name] = digest
    return versions


def _compute_version() -> str:
    versions = asset_version_map()
    # Stable across restarts and processes (no PYTHONHASHSEED dependence).
    return hashlib.sha256(json.dumps(versions, sort_keys=True).encode()).hexdigest()[:12]


@lru_cache(maxsize=1)
def current_asset_version() -> str:
    """Single build id computed once per process from the asset contents."""
    return _compute_version()


def reset_asset_version() -> None:
    """Forget the cached build id (tests, or after rebuilding assets in place)."""
    current_asset_version.cache_clear()


def split_asset_url(url: str) -> tuple[str, str]:
    """Return ``(path, query)`` for a local asset URL, dropping any ``?v=...``."""
    path, _, rest = url.partition("?")
    query = rest.split("#", 1)[0]
    kept = [part for part in query.split("&") if part and not part.startswith("v=")]
    return path, "&".join(kept)


def asset_urls_in_html(html: str) -> list[str]:
    """Every local (root-relative) asset path referenced by an HTML shell."""
    return sorted(
        {split_asset_url(match.group(2))[0] for match in _HTML_ASSET_REFERENCE.finditer(html)}
    )


def version_query(url: str, versions: dict[str, str]) -> str:
    """Add/refresh ``v=`` on a static asset URL; leaves non-hashed URLs alone."""
    path, query = split_asset_url(url)
    digest = versions.get(path)
    if not digest:
        return url
    return f"{path}?v={digest}" + (f"&{query}" if query else "")


def bust_static_urls(html: str, versions: dict[str, str] | None = None) -> str:
    """Version every static asset reference in an HTML page by content hash."""
    table = asset_version_map() if versions is None else versions
    return _HTML_ASSET_REFERENCE.sub(
        lambda match: match.group(1) + version_query(match.group(2), table),
        html,
    )


def render_static_page(name: str) -> str:
    """Read a shell from ``static/``, fill the placeholder and bust asset URLs."""
    html = (STATIC_DIR / name).read_text(encoding="utf-8")
    html = html.replace(_VERSION_PLACEHOLDER, current_asset_version())
    html = bust_static_urls(html)
    if _VERSION_PLACEHOLDER in html:  # pragma: no cover - authoring guard
        raise RuntimeError(f"{name} still contains {_VERSION_PLACEHOLDER}")
    return html


def static_page_response(name: str) -> HTMLResponse:
    """HTML shell response: per-file cache-busted asset URLs, never cached."""
    return HTMLResponse(render_static_page(name), headers={"Cache-Control": "no-store"})


def main() -> None:
    print(current_asset_version())


if __name__ == "__main__":
    main()
