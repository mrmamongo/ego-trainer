from ego.testing import case, rules

@case(
    args=({"lang": "ru", "ui": {"theme": "dark", "size": 12}}, {"ui": {"size": 14}}),
    expected={"lang": "ru", "ui": {"theme": "dark", "size": 14}},
    description='вложенный словарь сливается',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 1}, {"b": 2}),
    expected={"a": 1, "b": 2},
    description='разные ключи',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 1}, {"a": 2}),
    expected={"a": 2},
    description='пользователь побеждает',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({}, {"a": {"b": 1}}),
    expected={"a": {"b": 1}},
    description='пустые умолчания',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1}}, {}),
    expected={"a": {"b": 1}},
    description='пустые настройки пользователя',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({}, {}),
    expected={},
    description='всё пусто',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1}}, {"a": 5}),
    expected={"a": 5},
    description='значение пользователя вместо словаря',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 5}, {"a": {"b": 1}}),
    expected={"a": {"b": 1}},
    description='словарь пользователя вместо значения',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 1}, {"a": None}),
    expected={"a": None},
    description='None пользователя тоже побеждает',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"tags": ["a", "b"]}, {"tags": ["c"]}),
    expected={"tags": ["c"]},
    description='списки не сливаются',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": {"c": 1, "d": 2}}}, {"a": {"b": {"d": 3, "e": 4}}}),
    expected={"a": {"b": {"c": 1, "d": 3, "e": 4}}},
    description='три уровня',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"ui": {"size": 12}}, {"ui": {"size": 12}, "lang": "en"}),
    expected={"ui": {"size": 12}, "lang": "en"},
    description='общая ветка в defaults и user: результат всё равно независим',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((1, "ui"), (0, "ui")),),
)

@case(
    args=({"x": {"y": 1}}, {"x": {"z": 2}, "w": {"v": 3}}),
    expected={"x": {"y": 1, "z": 2}, "w": {"v": 3}},
    description='новая ветка пользователя и общая ветка вместе',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    hide_expected=True,
)


@rules(
    forbid_imports=["copy", "json"],
    require_functions=["given_deep_copy"],
    messages={
        "copy": "Модуль copy использовать нельзя: копию делает given_deep_copy",
        "json": "Модуль json использовать нельзя: копию делает given_deep_copy",
    },
)

def task_ns14_merge_settings(defaults, user):
    ...
