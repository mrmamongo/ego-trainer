"""Render the static landing with the single editable public brand configuration."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

_STATIC_DIR = Path(__file__).parent / "static"


def render_landing() -> str:
    brand = json.loads((_STATIC_DIR / "branding" / "brand.json").read_text(encoding="utf-8"))
    from ego_server.config import settings

    replacements = {
        "BRAND_NAME": escape(str(brand["name"])),
        "BRAND_DESCRIPTION": escape(str(brand["description"]), quote=True),
        # Brand assets are trusted, project-owned files; text fields are escaped.
        "BRAND_MARK": str(brand["mark"]),
        "BRAND_LOGO_URL": escape(str(brand["logo_url"]), quote=True),
        "FORGEJO_URL": escape(settings.forgejo_url, quote=True),
    }
    html = (_STATIC_DIR / "landing.html").read_text(encoding="utf-8")
    for key, value in replacements.items():
        html = html.replace("{{" + key + "}}", value)
    return html
