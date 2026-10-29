from ego.testing import case, rules

# --- старое поведение: структура та же, теперь внутри "data" ---

@case(
    args=({"a": 1, "b": 2}, ["a"]),
    expected={"data": {"b": 2}, "removed": ["a"]},
    description='удалить ключ верхнего уровня',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1, "c": 2}}, ["a", "b"]),
    expected={"data": {"a": {"c": 2}}, "removed": ["a.b"]},
    description='удалить вложенное значение',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

# --- новое: список удалённых путей в порядке удаления ---

@case(
    args=({"a": {"b": 1}}, ["a", "b"]),
    expected={"data": {}, "removed": ["a.b", "a"]},
    description='опустевшая ветка попадает в removed после значения',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 1}, ["x"]),
    expected={"data": {"a": 1}, "removed": []},
    description='нет такого ключа',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 1}, ["a", "b"]),
    expected={"data": {"a": 1}, "removed": []},
    description='на пути лежит число',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": {"c": 1}}, "d": 2}, ["a", "b", "c"]),
    expected={"data": {"d": 2}, "removed": ["a.b.c", "a.b", "a"]},
    description='цепочка из двух опустевших веток',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": {"c": 1}, "e": 2}}, ["a", "b", "c"]),
    expected={"data": {"a": {"e": 2}}, "removed": ["a.b.c", "a.b"]},
    description='сосед не даёт верхней ветке схлопнуться',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1, "c": 2}, "d": 3}, ["a"]),
    expected={"data": {"d": 3}, "removed": ["a"]},
    description='целая ветка одним путём',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {}, "b": 1}, ["a", "x"]),
    expected={"data": {"a": {}, "b": 1}, "removed": []},
    description='изначально пустая ветка не трогается',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": {}}, "c": 1}, ["a", "b"]),
    expected={"data": {"c": 1}, "removed": ["a.b", "a"]},
    description='удалили пустой словарь, и родитель опустел',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    hide_expected=True,
)

@case(
    args=({"x": {"y": {"z": {"w": 1}}}}, ["x", "y", "z", "w"]),
    expected={"data": {}, "removed": ["x.y.z.w", "x.y.z", "x.y", "x"]},
    description='длинная цепочка',
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

def task_ns13_delete_path(data, path):
    ...
