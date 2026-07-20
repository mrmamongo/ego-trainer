#!/usr/bin/env python3
"""Migrate docs/tasks to sidecar format with smoke @case coverage.

Writes:
  <task>.solution.py  — extracted from <details> (or kept if already present)
  <task>.tests.py     — smoke cases only (full / Hypothesis later)

Usage (from repo root):
  uv run python scripts/migrate_smoke_format.py
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

from ego.checker import _find_main_function
from ego.parser import parse_task_file

ROOT = Path("docs/tasks")

# task_id -> list of (args_tuple, description)
# expected is computed by executing the reference solution.
SMOKE: dict[str, list[tuple[tuple, str]]] = {
    "F1": [
        (([{"id": "B1", "severity": "critical", "title": "Crash"}],), "one critical"),
        (([],), "empty list"),
        (([{"id": "B1", "severity": "minor", "title": "Typo"}],), "no critical"),
    ],
    "F2": [
        (([{"email": "a@x.com", "active": True}, {"email": "b@x.com", "active": False}],), "filter active"),
        (([],), "empty"),
    ],
    "F3": [
        (([{"status": "pending"}, {"status": "done"}, {"status": "pending"}],), "two pending"),
        (([],), "empty"),
    ],
    "F4": [
        (([{"result": "passed"}, {"result": "passed"}],), "all passed"),
        (([{"result": "passed"}, {"result": "failed"}],), "one failed"),
        (([],), "empty is all passed"),
    ],
    "F5": [
        (({"items": [{"category": "vip"}, {"category": "normal"}]},), "has vip"),
        (({"items": [{"category": "normal"}]},), "no vip"),
        (({},), "no items key"),
    ],
    "1.1": [
        (([{"level": "ERROR"}, {"level": "INFO"}, {"level": "ERROR"}],), "two errors"),
        (([],), "empty"),
    ],
    "1.2": [
        (([{"level": "ERROR", "service": "api"}, {"level": "ERROR", "service": "api"}, {"level": "INFO", "service": "db"}],), "count by service"),
        (([],), "empty"),
    ],
    "1.3": [
        (([{"timestamp": "t1", "service": "api", "response_time_ms": 600}, {"timestamp": "t2", "service": "db", "response_time_ms": 100}],), "one slow"),
        (([],), "empty"),
    ],
    "1.4": [
        (([{"service": "api", "status": 500}, {"service": "api", "status": 200}, {"service": "db", "status": 500}],), "unique services"),
        (([],), "empty"),
    ],
    "1.5": [
        (([{"service": "api", "status": 200}, {"service": "api", "status": 500}],), "sla 50%"),
        (([],), "empty"),
    ],
    "A": [
        (
            (
                [{"run_id": "r1", "model": "m", "prompt": "p"}],
                [{"run_id": "r1", "chunk_id": "c1", "text": "hi"}],
                [{"run_id": "r1", "tokens_in": 10, "tokens_out": 5}],
            ),
            "basic merge",
        ),
        (([], [], []), "all empty"),
    ],
    "B": [
        (({"email": "a@b.com", "nested": {"x": 1}},), "dict with email"),
        (("plain",), "plain string"),
        (([],), "empty list"),
    ],
    "C": [
        (({"r1": {"model": "m", "chunks": [{"chunk_id": "c1", "text": "t"}]}},), "one run"),
        (({},), "empty"),
    ],
    "D1": [
        (([{"category": "food", "amount": 10}, {"category": "food", "amount": 5}],), "sum category"),
        (([],), "empty"),
    ],
    "D2": [
        (([{"sensor_id": "s1", "temperature": 90, "humidity": 10}],), "temp alert"),
        (([{"sensor_id": "s1", "temperature": 20, "humidity": 10}],), "no alert"),
    ],
    "D3": [
        (([{"build_id": "b1", "duration_sec": 10, "branch": "main", "status": "failed"}],), "one failed"),
        (([{"build_id": "b1", "duration_sec": 10, "branch": "main", "status": "ok"}],), "none failed"),
    ],
    "D4": [
        (([{"rarity": "rare", "qty": 2, "unit_price": 5}],), "value 10"),
        (([],), "empty"),
    ],
    "D5": [
        (([{"endpoint": "/a", "ms": 100}, {"endpoint": "/a", "ms": 300}],), "avg stats"),
        (([],), "empty"),
    ],
    "G1": [
        ((["a", "b", "a"],), "freq"),
        (([],), "empty"),
    ],
    "G2": [
        (({"a": 5, "b": 1}, 3), "min_count 3"),
        (({}, 1), "empty vocab"),
    ],
    "G3": [
        (([1, 2, 3, 4], 2), "truncate"),
        (([], 5), "empty"),
    ],
    "G4": [
        (([1, 0, 1], [1, 1, 1]), "2/3 accuracy"),
        (([], []), "empty"),
    ],
    "G5": [
        (([{"id": "s1", "tokens": [1, 2]}, {"id": "s2", "tokens": [1]}],), "group by len"),
        (([],), "empty"),
    ],
    "G6": [
        (([[1, 2], [1]], 0), "pad batch"),
        (([], 0), "empty batch"),
    ],
    "G7": [
        (({"a": 3.0, "b": 1.0, "c": 2.0}, 2), "top-2"),
        (({}, 1), "empty logits"),
    ],
    "H1": [
        (([{"name": "sword", "qty": 1}, {"name": "sword", "qty": 2}],), "stack"),
        (([],), "empty"),
    ],
    "H2": [
        (([{"item": "gold", "chance": 100, "min": 1, "max": 1}],), "always drop"),
        (([],), "empty drops"),
    ],
    "H3": [
        (({"class": "warrior", "stats": {"str": 5, "int": 1, "agi": 1}},), "warrior score"),
        (({"class": "mage", "stats": {"str": 1, "int": 5, "agi": 1}},), "mage score"),
    ],
    "H4": [
        (([{"weight": 2, "value": 5}, {"weight": 3, "value": 10}], 3), "capacity 3"),
        (([], 10), "empty items"),
    ],
    "H5": [
        ((1, 0, 150), "level up once"),
        ((1, 0, 0), "no xp"),
    ],
    "H6": [
        ((["sword", "shield", "potion"], ["p1", "p2"]), "round robin"),
        (([], ["p1"]), "no items"),
    ],
    "H7": [
        (([True, True, True],), "triple combo"),
        (([True, False, True],), "break combo"),
    ],
    "H8": [
        (({"ore": {"C": 7, "U": 2, "R": 0}},), "craft tiers"),
        (({},), "empty inventory"),
    ],
}


def _exec_expected(solution_py: str, func_name: str, args: tuple) -> Any:
    ns: dict[str, Any] = {}
    exec(solution_py, ns)  # noqa: S102 — trusted reference from our repo
    return ns[func_name](*args)


def _format_value(value: Any) -> str:
    """repr() that keeps ``float('inf')`` importable in generated .tests.py."""
    if isinstance(value, float) and value != value:  # NaN
        return "float('nan')"
    if value == float("inf"):
        return "float('inf')"
    if value == float("-inf"):
        return "float('-inf')"
    if isinstance(value, dict):
        items = ", ".join(f"{_format_value(k)}: {_format_value(v)}" for k, v in value.items())
        return "{" + items + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_format_value(v) for v in value) + "]"
    if isinstance(value, tuple):
        if len(value) == 1:
            return f"({_format_value(value[0])},)"
        return "(" + ", ".join(_format_value(v) for v in value) + ")"
    return repr(value)


def _write_tests(path: Path, func_name: str, cases: list[tuple[tuple, Any, str]]) -> None:
    lines = [
        '"""Smoke tests — generated by scripts/migrate_smoke_format.py.',
        "",
        "Full corpus / Hypothesis (@scenario) — later (epic 9u7).",
        '"""',
        "",
        "from ego.testing import case",
        "",
    ]
    for args, expected, desc in cases:
        lines.append("@case(")
        lines.append(f"    args={_format_value(args)},")
        lines.append(f"    expected={_format_value(expected)},")
        lines.append(f"    description={_format_value(desc)},")
        lines.append('    level="smoke",')
        lines.append(")")
    # signature: use *args so we don't need real param names
    params = ", ".join(f"a{i}" for i in range(max((len(c[0]) for c in cases), default=0))) or ""
    lines.append(f"def {func_name}({params}):")
    lines.append("    ...")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    missing_smoke = []
    for md in sorted(ROOT.rglob("*.md")):
        task = parse_task_file(md)
        func_name = _find_main_function(task.solution_py)
        if not func_name:
            raise SystemExit(f"no task_* in {md}")

        sol_path = md.with_suffix(".solution.py")
        if not sol_path.exists():
            sol_path.write_text(task.solution_py, encoding="utf-8")
            print(f"wrote {sol_path}")
        else:
            print(f"keep  {sol_path}")

        smoke = SMOKE.get(task.id)
        if not smoke:
            missing_smoke.append(task.id)
            continue

        computed: list[tuple[tuple, Any, str]] = []
        for args, desc in smoke:
            expected = _exec_expected(task.solution_py, func_name, args)
            computed.append((args, expected, desc))

        tests_path = md.with_suffix(".tests.py")
        _write_tests(tests_path, func_name, computed)
        print(f"wrote {tests_path} ({len(computed)} smoke)")

    if missing_smoke:
        raise SystemExit(f"missing smoke cases for: {missing_smoke}")
    print("done")


if __name__ == "__main__":
    main()
