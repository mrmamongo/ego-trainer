"""Markdown parser — .md (+ optional sidecars) -> Task.

Формат описан в docs/TESTS_DESIGN.md:
- ``<task>.md`` — условие
- ``<task>.solution.py`` — эталон (fallback: ``<details>`` в .md)
- ``<task>.tests.py`` — ``@case`` / hooks (path → ``Task.tests_file``)

Legacy: ``## Тесты`` literal → ``extra["tests_code"]`` (deprecated).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from ego.models import Task

# === Regexes / patterns ===

_TITLE_RE = re.compile(r"^# Задача\s+(\S+):\s*(.+)$")

# Секции H2 — используем для разбиения markdown на части.
_SECTION_RES: dict[str, re.Pattern[str]] = {
    "Условие": re.compile(r"^## Условие\s*$"),
    "Аргументы": re.compile(r"^## Аргументы\s*$"),
    "Возвращает": re.compile(r"^## Возвращает\s*$"),
    "Правила": re.compile(r"^## Правила\s*$"),
    "Пример": re.compile(r"^## Пример\s*$"),
    "Тесты": re.compile(r"^## Тесты\s*$"),
}

# Секции, попадающие в statement_md (всегда кроме Тесты).
_STATEMENT_SECTIONS = ("Условие", "Аргументы", "Возвращает", "Правила", "Пример")

# <details><summary>Эталонное решение</summary> ... ```python ... ```
_SOLUTION_RE = re.compile(
    r"<summary>\s*Эталонное решение\s*</summary>\s*"
    r"```python\n(.*?)```",
    re.DOTALL,
)

# Первый ```python блок внутри произвольного текста.
_CODE_BLOCK_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)

# def task_xxx(...): сигнатура + тело (для генерации stub).
_FUNC_RE = re.compile(
    r"^(def (task_\w+)\s*\([^)]*\)\s*:[^\n]*\n)"  # signature line
    r"((?:[ \t]+.*\n)*)",  # indented body
    re.MULTILINE,
)

# docstring в начале тела функции.
_DOCSTRING_RE = re.compile(
    r"^([ \t]+)(\"\"\".*?\"\"\"|'''.*?''')\s*\n",
    re.DOTALL,
)


# === Public API ===


def parse_task_file(path: Path, default_version: str = "1.0.0") -> Task:
    """Parse a .md task file into a Task object.

    Args:
        path: path to .md file.
        default_version: SemVer to assign if not in .md (default ``"1.0.0"``).

    Returns:
        Task with all fields populated.

    Raises:
        ValueError: if .md is malformed (missing required sections).
    """
    text = path.read_text(encoding="utf-8")
    return parse_task_text(text, path=path, default_version=default_version)


def parse_task_text(text: str, path: Path, default_version: str = "1.0.0") -> Task:
    """Parse .md text into a Task. See :func:`parse_task_file`."""
    # 0. Strip YAML frontmatter if present (ADR-0016 D16.6). Frontmatter
    #    is the source of truth for sync meta, but the parser still reads
    #    the body (statement/solution) the same way. Frontmatter fields
    #    (id/title/version/level/tags/breaking) are applied by the sync
    #    layer via :func:`ego.catalog.parse_task_frontmatter`; here we
    #    only strip it so legacy H1/bold parsing works on the body.
    text, _fm_consumed = _strip_frontmatter(text)

    lines = text.splitlines()

    # 1. Title from H1 + bold meta (Блок/Сложность/Темы). Bold meta is
    #    optional — in the new catalog layout (ADR-0016 D16.6) these
    #    fields come from YAML frontmatter + folder.yaml, not bold lines.
    #    The sync layer applies frontmatter overrides after parsing.
    task_id, title = _parse_title(lines[0] if lines else "")
    block, block_name = _parse_bold_meta_optional(lines, "Блок", default=slug_first_char(path.parent.name))
    level = _parse_bold_meta_optional(lines, "Сложность", default="easy")[0]
    tags_str = _parse_bold_meta_optional(lines, "Темы", default="")[0]
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]

    # 2. Slug = имя родительской директории (напр. "block_f_simple")
    slug = path.parent.name

    # 3. Разбиваем на секции по H2 заголовкам
    sections = _split_sections(lines)
    if "Условие" not in sections:
        raise ValueError(f"Missing '## Условие' section in {path}")

    # 4. statement_md = весь markdown КРОМЕ <details> (эталон) и ## Тесты
    statement_md = _build_statement_md(sections)

    # 5. solution_py — sidecar <task>.solution.py, fallback <details> in .md
    solution_py, from_sidecar = _load_solution(path, text)
    if not solution_py:
        raise ValueError(
            f"Missing solution: need {path.with_suffix('.solution.py').name} "
            f"or <details>Эталонное решение</summary> in {path}"
        )

    # 6. tests_file — sidecar <task>.tests.py; legacy ## Тесты → tests_code
    tests_file = _sidecar_path(path, ".tests.py")
    if tests_file is not None and not tests_file.is_file():
        tests_file = None
    test_cases_raw = _extract_tests_code(sections.get("Тесты", []))

    # 7. stub_py = генерируется из сигнатуры основной функции эталона
    stub_py = _generate_stub(solution_py, task_id)

    # 8. content_hash = sha256(statement_md + stub_py + solution_py)
    content_hash = _hash_content(statement_md, stub_py, solution_py)

    extra: dict = {"block_name": block_name}
    if from_sidecar:
        extra["solution_source"] = "sidecar"
    if test_cases_raw:
        extra["tests_code"] = test_cases_raw

    return Task(
        id=task_id,
        block=block,
        slug=slug,
        task_id=task_id,
        title=title,
        level=level,  # type: ignore[arg-type]
        tags=tags,
        version=default_version,
        content_hash=content_hash,
        md_path=path,
        statement_md=statement_md,
        stub_py=stub_py,
        solution_py=solution_py,
        tests_file=tests_file,
        extra=extra,
    )


# === Helpers ===


def _strip_frontmatter(text: str) -> tuple[str, bool]:
    """Strip a leading ``---\\n...\\n---\\n`` YAML frontmatter block.

    Returns ``(body_text, had_frontmatter)``. If no frontmatter present,
    returns ``(text, False)``. Does NOT parse the YAML — just removes it
    so the legacy H1/bold parsing works on the body. Frontmatter meta is
    applied separately by the sync layer (see :mod:`ego.catalog`).

    Per ADR-0016 D16.6: frontmatter is the source of truth for sync,
    but the parser still reads the body (statement/solution) the same way.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text, False
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            body = "\n".join(lines[i + 1 :]).lstrip("\n")
            return body, True
    # Unclosed frontmatter — leave text as is (let parser fail naturally).
    return text, False


def _parse_title(line: str) -> tuple[str, str]:
    """Parse ``# Задача <ID>: <Title>`` → ``(id, title)``."""
    m = _TITLE_RE.match(line)
    if not m:
        raise ValueError(f"Invalid title line: {line!r}")
    return m.group(1), m.group(2).strip()


def _parse_bold_meta(lines: list[str], key: str) -> tuple[str, str]:
    """Parse ``**<key>:** <value>`` (optionally ``— <rest>``).

    Ищет в первых 10 строках. Возвращает ``(value, rest)``.
    Raises ``ValueError`` if not found (legacy strict mode).
    """
    pattern = re.compile(rf"^\*\*{re.escape(key)}:\*\*\s*(.+?)(?:\s*—\s*(.+))?$")
    for line in lines[:10]:
        m = pattern.match(line)
        if m:
            val = m.group(1).strip()
            rest = (m.group(2) or "").strip()
            return val, rest
    raise ValueError(f"Missing **{key}:** in front-matter")


def _parse_bold_meta_optional(
    lines: list[str], key: str, *, default: str = ""
) -> tuple[str, str]:
    """Like :func:`_parse_bold_meta` but returns ``(default, "")`` if absent.

    Used for the new catalog layout (ADR-0016 D16.6) where bold meta may
    be missing — fields come from YAML frontmatter + folder.yaml instead.
    """
    try:
        return _parse_bold_meta(lines, key)
    except ValueError:
        return default, ""


def slug_first_char(name: str) -> str:
    """Derive a fallback block code from a directory slug.

    ``block_f_simple`` → ``F``, ``block_1_logs`` → ``1``, ``foo`` → ``F``.
    Used when ``**Блок:**`` is absent (new catalog layout).
    """
    parts = name.split("_")
    if len(parts) >= 2 and parts[0] == "block":
        return parts[1].upper()
    return name[:1].upper() if name else "?"


def _split_sections(lines: list[str]) -> dict[str, list[str]]:
    """Split markdown by ``## H2`` headers.

    Returns ``{section_name: [content_lines]}`` (без строки-заголовка).
    Строки до первого H2 заголовка теряются (title + meta).
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    current_lines: list[str] = []
    for line in lines:
        matched = False
        for name, regex in _SECTION_RES.items():
            if regex.match(line):
                if current is not None:
                    sections[current] = current_lines
                current = name
                current_lines = []
                matched = True
                break
        if not matched and current is not None:
            current_lines.append(line)
    if current is not None:
        sections[current] = current_lines
    return sections


def _strip_details(lines: list[str]) -> list[str]:
    """Remove ``<details>...</details>`` blocks from a list of lines."""
    result: list[str] = []
    in_details = False
    for line in lines:
        if not in_details and "<details>" in line.lower():
            in_details = True
            continue
        if in_details and "</details>" in line.lower():
            in_details = False
            continue
        if not in_details:
            result.append(line)
    return result


def _build_statement_md(sections: dict[str, list[str]]) -> str:
    """Build statement_md = everything except ``## Тесты`` and ``<details>``.

    Сохраняет секции Условие, Аргументы, Возвращает, Правила, Пример.
    Из всех секций вырезаются ``<details>`` блоки (эталон).
    """
    parts: list[str] = []
    for name in _STATEMENT_SECTIONS:
        if name not in sections:
            continue
        parts.append(f"## {name}\n")
        content = "\n".join(_strip_details(sections[name])).strip()
        if content:
            parts.append(content)
        parts.append("")  # blank line between sections
    return "\n".join(parts).strip()


def _sidecar_path(md_path: Path, suffix: str) -> Path:
    """``task_f1.md`` + ``.solution.py`` → ``task_f1.solution.py``."""
    # path.with_suffix('.solution.py') on 'task_f1.md' → 'task_f1.solution.py'
    return md_path.with_suffix(suffix)


def _load_solution(md_path: Path, text: str) -> tuple[str, bool]:
    """Load solution from sidecar or ``<details>``. Returns ``(code, from_sidecar)``."""
    sidecar = _sidecar_path(md_path, ".solution.py")
    if sidecar.is_file():
        code = sidecar.read_text(encoding="utf-8")
        if not code.endswith("\n"):
            code += "\n"
        return code, True
    return _extract_solution_code(text), False


def _extract_solution_code(text: str) -> str:
    """Extract Python code from ``<details><summary>Эталонное решение</summary>``.

    Возвращает код эталона (с завершающим ``\\n``) или пустую строку.
    """
    m = _SOLUTION_RE.search(text)
    if not m:
        return ""
    return m.group(1).rstrip("\n") + "\n"


def _extract_tests_code(tests_section_lines: list[str] | str) -> str:
    """Extract Python code from the ``## Тесты`` section's ```python``` block."""
    text = (
        tests_section_lines
        if isinstance(tests_section_lines, str)
        else "\n".join(tests_section_lines)
    )
    m = _CODE_BLOCK_RE.search(text)
    if not m:
        return ""
    return m.group(1).rstrip("\n") + "\n"


def _generate_stub(solution_py: str, task_id: str) -> str:
    """Generate student stub from reference solution.

    Стратегия: найти все ``def task_xxx(...)`` сигнатуры в эталоне,
    заменить тело на ``pass``. Сохранить docstring если есть в начале тела.
    Вспомогательные функции (не ``task_*``) — НЕ включать в stub.
    """
    stub_parts: list[str] = []
    for m in _FUNC_RE.finditer(solution_py):
        sig = m.group(1).rstrip()
        body = m.group(3)
        ds = _DOCSTRING_RE.match(body)
        if ds:
            indent = ds.group(1)
            stub_parts.append(sig)
            stub_parts.append(f"{indent}{ds.group(2)}")
            stub_parts.append(f"{indent}pass")
        else:
            stub_parts.append(sig)
            stub_parts.append("    pass")
        stub_parts.append("")  # blank line between functions

    if not stub_parts:
        # Fallback: ничего не нашли — возвращаем эталон как есть.
        return solution_py
    return "\n".join(stub_parts).rstrip() + "\n"


def _hash_content(statement_md: str, stub_py: str, solution_py: str) -> str:
    """sha256 of concatenated content with null-byte separators, hex digest."""
    h = hashlib.sha256()
    h.update(statement_md.encode("utf-8"))
    h.update(b"\x00")
    h.update(stub_py.encode("utf-8"))
    h.update(b"\x00")
    h.update(solution_py.encode("utf-8"))
    return h.hexdigest()
