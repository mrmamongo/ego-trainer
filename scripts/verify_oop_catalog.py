"""Check the «Python: ООП» pack through the real parser and sandbox runner.

Same checks as ``scripts.verify_start_catalog``, for project ``python-oop``.
Run from the repository with ``python -m scripts.verify_oop_catalog``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.verify_start_catalog import verify

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "docs/tasks/OOP/catalog"

EXPECTED_IDS = {
    "01_classes": [f"CL{n:02}" for n in range(1, 21)],
    "02_dataclasses": [f"DC{n:02}" for n in range(1, 17)],
    "04_class_methods": [f"CM{n:02}" for n in range(1, 19)],
    "05_magic_compare": [f"MG{n:02}" for n in range(1, 19)],
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    rows = verify(
        args.catalog,
        args.timeout,
        project_id="python-oop",
        expected_ids=EXPECTED_IDS,
        checkpoint_folders=set(),
    )
    print(json.dumps({"tasks": len(rows), "ok": True}))


if __name__ == "__main__":
    main()
