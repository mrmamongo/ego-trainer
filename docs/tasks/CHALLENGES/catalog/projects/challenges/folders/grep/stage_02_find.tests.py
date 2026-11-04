"""Этап 2: поиск по списку строк (импорт search.find_matches)."""

from ego.testing import case, rules


@rules(require_functions=["find_matches"])
@case(
    target="search.find_matches",
    args=(["INFO start", "ERROR disk", "INFO ok", "ERROR net"], "ERROR"),
    expected=[(2, "ERROR disk"), (4, "ERROR net")],
    description="номера строк считаются с единицы",
)
def task_gr02_numbers():
    ...


@case(
    target="search.find_matches",
    args=(["a", "b", "c"], "zzz"),
    expected=[],
    description="ничего не найдено: пустой список",
)
def task_gr02_none():
    ...


@case(
    target="search.find_matches",
    args=(["cat", "dog", "cow"], "c"),
    expected=[(1, "cat"), (3, "cow")],
    description="несколько совпадений, порядок как в списке",
)
def task_gr02_several():
    ...


@case(
    target="search.find_matches",
    args=(["cat\n", "dog\n", "cow\n"], "o"),
    expected=[(2, "dog"), (3, "cow")],
    description='"\\n" на конце строки в результат не попадает',
    level="full",
)
def task_gr02_newline():
    ...


@case(
    target="search.find_matches",
    args=(["last"], "last"),
    expected=[(1, "last")],
    description="список из одной строки",
    level="full",
)
def task_gr02_single():
    ...


@case(
    target="search.find_matches",
    args=([], "x"),
    expected=[],
    description="пустой список строк",
    level="full",
)
def task_gr02_empty_list():
    ...


@case(
    target="search.find_matches",
    args=(["one", "two", "three"], ""),
    expected=[(1, "one"), (2, "two"), (3, "three")],
    description="пустой шаблон подходит ко всем строкам",
    level="full",
)
def task_gr02_empty_pattern():
    ...


@case(
    target="search.find_matches",
    args=(["Error", "error", "ERROR"], "error"),
    expected=[(2, "error")],
    description="большие и маленькие буквы различаются",
    level="full",
)
def task_gr02_case():
    ...


@case(
    target="search.find_matches",
    args=(["a b", "ab", "a  b"], "a b"),
    expected=[(1, "a b")],
    description="пробелы в шаблоне считаются как обычные символы",
    check_inputs_unchanged=True,
    level="full",
)
def task_gr02_inputs():
    ...
