"""ego-tui CLI — separate entry-point for the TUI.

Implemented in the ``ego-trainer-x4f`` epic (post-MVP). This is a minimal
stub so the ``ego-tui`` console script (declared in ``pyproject.toml``)
resolves after ``uv sync`` instead of erroring with "module not found".
Per ADR-0001 D13.
"""

from __future__ import annotations

import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="ego-tui", description="Ego TUI (textual)."
    )
    parser.add_argument(
        "--version", action="version", version="ego-tui 0.1.0"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="start",
        help="start (default)",
    )
    parser.parse_args(argv)
    print(
        "ego-tui is not implemented yet (see beads ego-trainer-x4f epic)",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
