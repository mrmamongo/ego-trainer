"""Tests for ego.catalog — YAML models + parsers (ADR-0016 D16.6)."""

from __future__ import annotations

import pytest

from ego.catalog import (
    CatalogEntry,
    parse_catalog,
    parse_folder,
    parse_project,
    parse_task_frontmatter,
    split_frontmatter,
)


# === catalog.yaml ===


def test_parse_catalog_minimal():
    cat = parse_catalog("schema_version: 1\nprojects: []\n")
    assert cat.schema_version == 1
    assert cat.projects == []


def test_parse_catalog_with_projects():
    text = """
schema_version: 1
projects:
  - id: junior-core
    path: projects/junior-core
    enabled: true
  - id: llm-track
    path: projects/llm-track
    enabled: false
"""
    cat = parse_catalog(text)
    assert len(cat.projects) == 2
    assert cat.projects[0] == CatalogEntry(
        id="junior-core", path="projects/junior-core", enabled=True
    )
    assert cat.projects[1].enabled is False


def test_parse_catalog_unsupported_schema_version():
    with pytest.raises(ValueError, match="Unsupported"):
        parse_catalog("schema_version: 2\nprojects: []\n")


def test_parse_catalog_empty_string():
    """Empty YAML → empty catalog (not an error)."""
    cat = parse_catalog("")
    assert cat.projects == []


def test_parse_catalog_not_a_mapping():
    with pytest.raises(ValueError, match="mapping"):
        parse_catalog("- just\n- a\n- list\n")


# === project.yaml ===


def test_parse_project_full():
    text = """
id: junior-core
name: "Junior Core"
description: "Базовый трек: паттерны → логи → домены"
version: "1.2.0"
order: 10
default_locale: ru
tags: [python, junior]
version_policy: declare
"""
    proj = parse_project(text)
    assert proj.id == "junior-core"
    assert proj.name == "Junior Core"
    assert proj.version == "1.2.0"
    assert proj.order == 10
    assert proj.tags == ["python", "junior"]
    assert proj.version_policy == "declare"


def test_parse_project_minimal():
    proj = parse_project("id: x\nname: X\n")
    assert proj.id == "x"
    assert proj.name == "X"
    assert proj.version == "1.0.0"
    assert proj.version_policy == "declare"


def test_parse_project_ignores_unknown_fields():
    """extra='ignore' — unknown YAML keys are silently dropped."""
    proj = parse_project("id: x\nname: X\nfuture_field: 42\n")
    assert proj.id == "x"


# === folder.yaml ===


def test_parse_folder_full():
    text = """
id: block_f_simple
code: F
name: "Базовые паттерны"
description: "find, filter, count, all/any"
order: 10
level: easy
"""
    folder = parse_folder(text)
    assert folder.id == "block_f_simple"
    assert folder.code == "F"
    assert folder.level == "easy"


def test_parse_folder_minimal():
    folder = parse_folder("id: x\ncode: X\nname: X\n")
    assert folder.id == "x"
    assert folder.code == "X"
    assert folder.level is None


# === frontmatter split ===


def test_split_frontmatter_present():
    md = "---\nid: F1\ntitle: Test\nversion: 1.0.0\nlevel: easy\n---\n\n# Body\n"
    fm, body = split_frontmatter(md)
    assert fm == {"id": "F1", "title": "Test", "version": "1.0.0", "level": "easy"}
    assert body.startswith("# Body")


def test_split_frontmatter_absent():
    md = "# Задача F1: Hello\n\n## Условие\n..."
    fm, body = split_frontmatter(md)
    assert fm is None
    assert body == md


def test_split_frontmatter_unclosed_raises():
    md = "---\nid: F1\ntitle: Test\n\n# Body without closing delim\n"
    with pytest.raises(ValueError, match="Unclosed"):
        split_frontmatter(md)


def test_split_frontmatter_invalid_yaml_raises():
    md = "---\nid: : : broken\n---\nbody\n"
    with pytest.raises(ValueError, match="Invalid frontmatter"):
        split_frontmatter(md)


def test_split_frontmatter_not_mapping():
    md = "---\n- just\n- a\n- list\n---\nbody\n"
    with pytest.raises(ValueError, match="mapping"):
        split_frontmatter(md)


# === parse_task_frontmatter ===


def test_parse_task_frontmatter_present():
    md = (
        "---\n"
        "id: F1\n"
        'title: "Найди первый критический баг"\n'
        "version: 1.1.0\n"
        "level: easy\n"
        "tags: [find, linear search]\n"
        "breaking: false\n"
        "---\n\n"
        "# Задача F1: ...\n"
    )
    fm, body = parse_task_frontmatter(md)
    assert fm is not None
    assert fm.id == "F1"
    assert fm.title == "Найди первый критический баг"
    assert fm.version == "1.1.0"
    assert fm.level == "easy"
    assert fm.tags == ["find", "linear search"]
    assert fm.breaking is False
    assert body.startswith("# Задача F1")


def test_parse_task_frontmatter_absent():
    md = "# Задача F1: Hello\n"
    fm, body = parse_task_frontmatter(md)
    assert fm is None
    assert body == md


def test_parse_task_frontmatter_optional_fields_default():
    md = "---\nid: X1\ntitle: X\n---\n\nbody\n"
    fm, _ = parse_task_frontmatter(md)
    assert fm is not None
    assert fm.version == "1.0.0"
    assert fm.level == "easy"
    assert fm.tags == []
    assert fm.folder is None
    assert fm.breaking is False
