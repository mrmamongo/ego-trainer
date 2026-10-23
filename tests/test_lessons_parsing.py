"""Tests for theory cards — lesson frontmatter + walker discovery.

Covers ``lesson_*.md`` parsing in :mod:`ego.catalog`,
:func:`ego.content_repo.discover_repo` (catalog mode only; legacy ignores
lessons) and the task ``theory`` frontmatter field.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ego.catalog import (
    CONTENT_ID_RE,
    TaskFrontmatter,
    lesson_content_hash,
    parse_lesson_frontmatter,
    parse_task_frontmatter,
)
from ego.content_repo import discover_repo


# === parse_lesson_frontmatter ===


def test_parse_lesson_full():
    md = (
        "---\n"
        "id: roles-accumulator\n"
        'title: "Накопитель"\n'
        "order: 2\n"
        'version: "1.1.0"\n'
        "---\n\n"
        "# Накопитель\n\nПеременная-сумматор растёт в цикле.\n"
    )
    fm, body = parse_lesson_frontmatter(md)
    assert fm.id == "roles-accumulator"
    assert fm.title == "Накопитель"
    assert fm.order == 2
    assert fm.version == "1.1.0"
    assert "Переменная-сумматор" in body
    assert not body.startswith("---")


def test_parse_lesson_defaults():
    fm, body = parse_lesson_frontmatter("---\nid: x\n---\n\n# Заголовок\n\nТекст\n")
    assert fm.order == 0
    assert fm.version == "1.0.0"
    # title falls back to the first H1 of the body.
    assert fm.title == "Заголовок"
    assert body.startswith("# Заголовок")


def test_parse_lesson_ignores_unknown_fields():
    fm, _ = parse_lesson_frontmatter("---\nid: x\ntitle: X\nfuture: 1\n---\nbody\n")
    assert fm.id == "x"


@pytest.mark.parametrize(
    ("md", "match"),
    [
        ("# No frontmatter\n", "frontmatter"),
        ("---\ntitle: X\n---\nbody\n", "id"),
        ("---\nid: : : broken\n---\nbody\n", "Invalid frontmatter"),
        ("---\nid: x\n\nno closing delimiter\n", "Unclosed"),
    ],
)
def test_parse_lesson_rejects_bad_cards(md: str, match: str):
    with pytest.raises(ValueError, match=match):
        parse_lesson_frontmatter(md)


def test_lesson_content_hash_tracks_body_and_meta():
    fm1, body1 = parse_lesson_frontmatter("---\nid: x\ntitle: X\n---\nbody one\n")
    fm2, body2 = parse_lesson_frontmatter("---\nid: x\ntitle: X\n---\nbody two\n")
    fm_title, body3 = parse_lesson_frontmatter("---\nid: x\ntitle: Y\n---\nbody one\n")
    assert lesson_content_hash(fm1, body1) == lesson_content_hash(fm1, body1)
    assert len(lesson_content_hash(fm1, body1)) == 64
    assert lesson_content_hash(fm1, body1) != lesson_content_hash(fm2, body2)
    assert lesson_content_hash(fm1, body1) != lesson_content_hash(fm_title, body3)


# === task theory ===


def test_task_frontmatter_theory_defaults_to_empty():
    fm = TaskFrontmatter(id="F1", title="T")
    assert fm.theory == []
    parsed, _ = parse_task_frontmatter("---\nid: F1\ntitle: T\n---\nbody\n")
    assert parsed is not None and parsed.theory == []


def test_task_frontmatter_parses_ordered_theory_ids():
    fm, _ = parse_task_frontmatter(
        "---\nid: F1\ntitle: T\ntheory: [roles-accumulator, roles-counter]\n---\nbody\n"
    )
    assert fm is not None
    assert fm.theory == ["roles-accumulator", "roles-counter"]


def test_content_id_pattern_is_url_safe():
    import re

    for ok in ("roles-accumulator", "L01", "1.5", "a_b-c.d"):
        assert re.fullmatch(CONTENT_ID_RE, ok), ok
    for bad in ("", "-leading", "a/b", "a b", "x" * 65, "lessons/../x"):
        assert not re.fullmatch(CONTENT_ID_RE, bad), bad


# === Walker ===


@pytest.fixture
def lesson_repo(tmp_path: Path) -> Path:
    """Catalog repo: one project, two folders, lessons + tasks."""
    root = tmp_path / "ego-tasks"
    (root / "projects" / "junior" / "folders" / "a_block").mkdir(parents=True)
    (root / "projects" / "junior" / "folders" / "b_block").mkdir(parents=True)
    (root / "catalog.yaml").write_text(
        "schema_version: 1\nprojects:\n  - id: junior\n    path: projects/junior\n",
        encoding="utf-8",
    )
    (root / "projects" / "junior" / "project.yaml").write_text(
        "id: junior\nname: Junior\nversion_policy: declare\n", encoding="utf-8"
    )
    a = root / "projects" / "junior" / "folders" / "a_block"
    b = root / "projects" / "junior" / "folders" / "b_block"
    (a / "folder.yaml").write_text("id: a_block\ncode: A\nname: A\norder: 1\n", encoding="utf-8")
    (b / "folder.yaml").write_text("id: b_block\ncode: B\nname: B\norder: 2\n", encoding="utf-8")
    (a / "lesson_roles.md").write_text(
        "---\nid: roles\ntitle: Roles\norder: 1\n---\n# Roles\n\nText.\n", encoding="utf-8"
    )
    (a / "lesson_broken.md").write_text("# no frontmatter\n", encoding="utf-8")
    (b / "lesson_loops.md").write_text("---\nid: loops\norder: 0\n---\n# Loops\n", encoding="utf-8")
    (b / "task_b1.md").write_text(
        "---\nid: B1\ntitle: T\ntheory: [roles]\n---\n\n"
        "# Задача B1: T\n\n## Условие\nGo.\n",
        encoding="utf-8",
    )
    return root


def test_discover_lessons_catalog_mode(lesson_repo: Path):
    cat = discover_repo(lesson_repo)
    assert cat.is_legacy is False
    lessons = {(lesson.project_id, lesson.folder_id, lesson.md_path.name): lesson
               for lesson in cat.all_lessons}
    roles = lessons[("junior", "a_block", "lesson_roles.md")]
    assert roles.frontmatter is not None
    assert roles.frontmatter.id == "roles"
    assert "Text." in roles.body_md
    broken = lessons[("junior", "a_block", "lesson_broken.md")]
    assert broken.frontmatter is None
    assert "frontmatter" in broken.error
    loops = lessons[("junior", "b_block", "lesson_loops.md")]
    assert loops.frontmatter is not None
    assert loops.frontmatter.title == "Loops"  # from H1
    # Tasks are unaffected by lesson files living next to them.
    assert [t.frontmatter.id for t in cat.all_tasks] == ["B1"]


def test_discover_legacy_mode_ignores_lessons(tmp_path: Path):
    block = tmp_path / "block_f_simple"
    block.mkdir()
    (block / "lesson_x.md").write_text("---\nid: x\n---\nbody\n", encoding="utf-8")
    cat = discover_repo(tmp_path)
    assert cat.is_legacy is True
    assert cat.all_lessons == []
    assert all(f.lessons == [] for f in cat.projects[0].folders)
