from ego.testing import case, rules

@case(
    args=({"a": 1, "b": 2}, ["a"]),
    expected={"b": 2},
    description='удалить ключ верхнего уровня',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1, "c": 2}}, ["a", "b"]),
    expected={"a": {"c": 2}},
    description='удалить вложенное значение',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1}}, ["a", "b"]),
    expected={},
    description='опустевшая ветка убирается',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 1}, ["x"]),
    expected={"a": 1},
    description='нет такого ключа',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1}}, ["a", "x"]),
    expected={"a": {"b": 1}},
    description='нет ключа в глубине',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 1}, ["a", "b"]),
    expected={"a": 1},
    description='на пути лежит число',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": {"c": 1}}, "d": 2}, ["a", "b", "c"]),
    expected={"d": 2},
    description='опустели две ветки подряд',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": {"c": 1}, "e": 2}}, ["a", "b", "c"]),
    expected={"a": {"e": 2}},
    description='сосед не даёт ветке схлопнуться',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1, "c": 2}, "d": 3}, ["a"]),
    expected={"d": 3},
    description='удалить целую ветку',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {}, "b": 1}, ["a", "x"]),
    expected={"a": {}, "b": 1},
    description='изначально пустая ветка не трогается',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": {}}, "c": 1}, ["a", "b"]),
    expected={"c": 1},
    description='удалили пустой словарь, и родитель опустел',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    hide_expected=True,
)

@case(
    args=({"a": {"lang": "ru"}, "b": {"lang": "ru"}}, ["a", "lang"]),
    expected={"b": {"lang": "ru"}},
    description='общая ветка у двух ключей',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, "b"), (0, "a")),),
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

def task_ns09_delete_path(data, path):
    ...
