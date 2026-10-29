from ego.testing import case, rules

@case(
    args=({"a": 1}, ["a"], 2),
    expected={"a": 2},
    description='заменить значение верхнего уровня',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1}}, ["a", "b"], 2),
    expected={"a": {"b": 2}},
    description='заменить вложенное значение',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1}}, ["a", "c"], 5),
    expected={"a": {"b": 1, "c": 5}},
    description='добавить ключ в существующую ветку',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({}, ["x", "y", "z"], 1),
    expected={"x": {"y": {"z": 1}}},
    description='создать недостающие ветки',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 1, "b": {"c": 2}}, ["a"], 0),
    expected={"a": 0, "b": {"c": 2}},
    description='соседняя ветка сохраняется',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 5}, ["a", "b"], 1),
    expected={"a": {"b": 1}},
    description='число на пути заменяется словарём',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1}}, ["a"], 3),
    expected={"a": 3},
    description='словарь заменяется значением',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"lang": "ru"}, "b": {"lang": "ru"}}, ["a", "lang"], "en"),
    expected={"a": {"lang": "en"}, "b": {"lang": "ru"}},
    description='общая ветка у двух ключей: меняется только выбранный',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, "b"), (0, "a")),),
)

@case(
    args=({"k": {"m": {"n": 1}, "p": [2]}}, ["k", "m", "q"], None),
    expected={"k": {"m": {"n": 1, "q": None}, "p": [2]}},
    description='записать None и сохранить список рядом',
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

def task_ns08_set_path(data, path, value):
    ...
