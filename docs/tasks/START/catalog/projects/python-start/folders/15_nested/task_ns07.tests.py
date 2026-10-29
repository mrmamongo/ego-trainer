from ego.testing import case

@case(
    args=({"profile": {"settings": {"lang": "ru"}, "age": 30}}, ["profile", "settings", "lang"], "нет"),
    expected="ru",
    description='путь найден',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"profile": {"settings": {"lang": "ru"}}}, ["profile", "theme"], "нет"),
    expected="нет",
    description='ключа нет: default',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"a": 1}, ["a"], 0),
    expected=1,
    description='путь из одного ключа',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"a": 5}, ["a", "b"], "-"),
    expected="-",
    description='после "a" лежит число, а не словарь',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"a": "text"}, ["a", "b"], "-"),
    expected="-",
    description='после "a" лежит строка',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"a": [1, 2]}, ["a", "x"], "-"),
    expected="-",
    description='после "a" лежит список',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"a": 1}, [], "-"),
    expected={"a": 1},
    description='пустой путь: сам словарь',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({}, ["a"], 7),
    expected=7,
    description='пустой словарь',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"a": None}, ["a"], "нет"),
    expected=None,
    description='значение None есть, это не default',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"a": {"b": 0}}, ["a", "b"], 99),
    expected=0,
    description='ноль это настоящее значение',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    hide_expected=True,
)

@case(
    args=({"a": {"b": ""}, "c": False}, ["c"], 99),
    expected=False,
    description='False это настоящее значение',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    hide_expected=True,
)


def task_ns07_get_path(data, path, default):
    ...
