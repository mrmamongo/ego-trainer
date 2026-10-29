#!/usr/bin/env python3
"""Verify that every static asset the public pages reference is served.

Fetches ``/``, ``/panel``, ``/ide`` and ``/student`` from a running server (CI
smoke, a release candidate, or production behind the proxy) and asserts that
each local ``/static/...`` reference in the HTML -- and every ``/static/...``
URL referenced from the pages' own CSS or JS -- returns HTTP 200 with a
non-empty body.

Usage::

    python scripts/check_static_assets.py http://127.0.0.1:8000

Exit code 0 means every page and asset is fine; 1 lists the failures.

Point it at an HTML directory instead of a URL to check a build without
starting the server (the ``/static`` file that will be embedded is
``<dir>/static``)::

    python scripts/check_static_assets.py --local-dir ego_server/static
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

PAGES = ("/", "/panel", "/ide", "/student")
DEFAULT_TIMEOUT = 20.0

# src/href attributes and url(...) values that point at a local root path.
_HTML_REFERENCE = re.compile(
    r"""((?:src|href)\s*=\s*["']|url\(\s*["']?)(/[^"'\s)]+)""", re.IGNORECASE
)
# Code references a concrete file ("/static/branding/brand.json"), not a
# directory prefix used in checks like startsWith('/static/branding/').
_QUOTED_URL = re.compile(
    r"""["'](/static/[^"'\s?#]+\.(?:css|js|json|svg|png|ico|ttf|woff2?))["']"""
)
_CSS_URL = re.compile(r"""url\(\s*["']?(/[^"')\s]+)""", re.IGNORECASE)
# Assets loaded from code rather than page markup (workers, lazy imports).
_SKIPPED_ASSET_EXTENSIONS = (".map",)


def local_paths(html: str) -> set[str]:
    """Root-relative paths referenced by ``src``/``href``/``url(...)`` in HTML."""
    return {_strip_query(match.group(2)) for match in _HTML_REFERENCE.finditer(html)}


def _strip_query(url: str) -> str:
    return url.split("?", 1)[0].split("#", 1)[0]


def _is_static(url: str) -> bool:
    return url.startswith("/static/") and not url.endswith(_SKIPPED_ASSET_EXTENSIONS)


def transitive_static_paths(path: str, body: str) -> set[str]:
    """``/static`` URLs referenced *inside* a fetched CSS/JS asset."""
    if path.endswith(".css"):
        found = {_strip_query(m.group(1)) for m in _CSS_URL.finditer(body)}
    elif path.endswith(".js"):
        found = {_strip_query(m.group(1)) for m in _QUOTED_URL.finditer(body)}
    else:
        return set()
    return {url for url in found if _is_static(url)}


class Fetcher:
    """HTTP fetcher for a base URL."""

    def __init__(self, base_url: str, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str) -> tuple[int, str, bytes]:
        url = self.base_url + path
        request = urllib.request.Request(url, headers={"User-Agent": "cogito-static-check"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, response.geturl(), response.read()
        except urllib.error.HTTPError as error:
            return error.code, url, error.read()
        except (urllib.error.URLError, OSError) as error:
            raise SystemExit(f"cannot reach {url}: {error}") from error


class LocalFetcher:
    """Fetcher over an ``ego_server/static`` directory (no server needed).

    Page shells go through the server's own renderer when ``ego_server`` is
    importable, so the ``{{STATIC_ASSET_VERSION}}`` placeholders are filled in
    exactly as they are in production; otherwise the raw file is checked.
    """

    _PAGE_FILES = {"/": "landing.html", "/panel": "admin.html", "/ide": "ide.html"}

    def __init__(self, static_dir: Path) -> None:
        self.static_dir = static_dir
        try:
            from ego_server import static_pages
        except ImportError:
            self.render = None
        else:
            self.render = static_pages.render_static_page

    def _page(self, filename: str) -> bytes:
        if self.render is not None and filename != "landing.html":
            return self.render(filename).encode("utf-8")
        return (self.static_dir / filename).read_bytes()

    def get(self, path: str) -> tuple[int, str, bytes]:
        if path in self._PAGE_FILES:
            return 200, path, self._page(self._PAGE_FILES[path])
        if path in ("/student", "/student/"):
            return 200, path, (self.static_dir / "student.html").read_bytes()
        file = self.static_dir / path.removeprefix("/static/")
        if not file.is_file():
            return 404, path, b""
        return 200, path, file.read_bytes()


def check_pages(fetch, pages=PAGES) -> list[str]:
    """Return human-readable failures; empty means healthy."""
    failures: list[str] = []
    # Assets may be shared by pages/CSS/JS: fetch each once.
    fetched: dict[str, tuple[int, bytes]] = {}
    reachable: set[str] = set()

    def fetch_asset(path: str) -> tuple[int, bytes]:
        if path not in fetched:
            status, _, body = fetch.get(path)
            fetched[path] = (status, body)
        return fetched[path]

    for page in pages:
        status, _, body = fetch.get(page)
        if status != 200:
            failures.append(f"page {page}: HTTP {status}")
            continue
        html = body.decode("utf-8", "replace")
        for path in sorted(local_paths(html)):
            if not _is_static(path):
                continue
            reachable.add(path)
            asset_status, asset_body = fetch_asset(path)
            if asset_status != 200:
                failures.append(f"{page} -> {path}: HTTP {asset_status}")
                continue
            if not asset_body:
                failures.append(f"{page} -> {path}: empty body")
                continue
            for nested in sorted(
                transitive_static_paths(path, asset_body.decode("utf-8", "replace"))
            ):
                if nested in reachable:
                    continue
                reachable.add(nested)
                nested_status, _ = fetch_asset(nested)
                if nested_status != 200:
                    failures.append(f"{path} -> {nested}: HTTP {nested_status}")
        print(f"ok   {page}: {len(local_paths(html))} local references")
    print(f"checked {len(reachable)} static assets")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("base_url", nargs="?", help="server root, e.g. http://127.0.0.1:8000")
    parser.add_argument(
        "--local-dir",
        type=Path,
        help="check an ego_server/static directory instead of a running server",
    )
    parser.add_argument(
        "--pages",
        nargs="+",
        default=list(PAGES),
        help=f"pages to check (default: {' '.join(PAGES)})",
    )
    args = parser.parse_args(argv)
    if bool(args.base_url) == bool(args.local_dir):
        parser.error("pass exactly one of base_url or --local-dir")

    fetch = LocalFetcher(args.local_dir) if args.local_dir else Fetcher(args.base_url)
    label = str(args.local_dir) if args.local_dir else args.base_url
    print(f"checking {label}")
    failures = check_pages(fetch, args.pages)
    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        print(f"{len(failures)} failure(s)")
        return 1
    print("all referenced static assets are served")
    return 0


if __name__ == "__main__":
    sys.exit(main())
