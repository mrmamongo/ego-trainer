"""Этап 1: совпадение строки с шаблоном (импорт matcher.matches)."""

from ego.testing import case, rules


@rules(
    require_functions=["matches"],
    forbid_nodes=["ClassDef"],
    messages={"ClassDef": "В этом челлендже классы не нужны: хватит функций и модулей"},
)
@case(
    target="matcher.matches",
    args=("hello world", "wor"),
    expected=True,
    description="шаблон есть в середине строки",
)
def task_gr01_found():
    ...


@case(
    target="matcher.matches",
    args=("hello world", "xyz"),
    expected=False,
    description="шаблона в строке нет",
)
def task_gr01_missing():
    ...


@case(
    target="matcher.matches",
    args=("hello", "hello"),
    expected=True,
    description="шаблон равен всей строке",
)
def task_gr01_whole():
    ...


@case(
    target="matcher.matches",
    args=("Hello", "hello"),
    expected=False,
    description="большие и маленькие буквы различаются",
    level="full",
)
def task_gr01_case():
    ...


@case(
    target="matcher.matches",
    args=("hello", ""),
    expected=True,
    description="пустой шаблон есть в любой строке",
    level="full",
)
def task_gr01_empty_pattern():
    ...


@case(
    target="matcher.matches",
    args=("", "a"),
    expected=False,
    description="в пустой строке непустой шаблон не найти",
    level="full",
)
def task_gr01_empty_line():
    ...


@case(
    target="matcher.matches",
    args=("abc", "abcd"),
    expected=False,
    description="шаблон длиннее строки",
    level="full",
)
def task_gr01_longer():
    ...


@case(
    target="matcher.matches",
    args=("disk is full", "is full"),
    expected=True,
    description="шаблон с пробелом",
    level="full",
)
def task_gr01_space():
    ...


@case(
    target="matcher.matches",
    args=("abcabc", "cab"),
    expected=True,
    description="шаблон на стыке повторов",
    level="full",
)
def task_gr01_overlap():
    ...
