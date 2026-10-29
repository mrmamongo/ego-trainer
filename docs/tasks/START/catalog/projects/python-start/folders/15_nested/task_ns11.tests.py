from ego.testing import case, rules

# --- старое поведение: запись и создание веток, теперь в обёртке done ---

@case(
    args=({"a": {"b": 1}}, ["a", "b"], 2),
    expected={"status": "done", "data": {"a": {"b": 2}}, "reason": None, "at": None},
    description='старое: заменить вложенное значение',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({}, ["x", "y"], 1),
    expected={"status": "done", "data": {"x": {"y": 1}}, "reason": None, "at": None},
    description='старое: создать недостающие ветки',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

# --- новое поведение: отказ ---

@case(
    args=({"a": 5}, ["a", "b"], 1),
    expected={"status": "rejected", "data": {"a": 5}, "reason": "not_a_dict", "at": "a"},
    description='на пути лежит число',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 5}}, ["a", "b", "c"], 1),
    expected={"status": "rejected", "data": {"a": {"b": 5}}, "reason": "not_a_dict", "at": "a.b"},
    description='отказ на втором шаге: at с точкой',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": [1]}, ["a", "x"], 1),
    expected={"status": "rejected", "data": {"a": [1]}, "reason": "not_a_dict", "at": "a"},
    description='на пути лежит список',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": None}, ["a", "x"], 1),
    expected={"status": "rejected", "data": {"a": None}, "reason": "not_a_dict", "at": "a"},
    description='на пути лежит None',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 5}}, ["a", "b"], 6),
    expected={"status": "done", "data": {"a": {"b": 6}}, "reason": None, "at": None},
    description='последний ключ можно записать поверх числа',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": 1}}, ["a"], 3),
    expected={"status": "done", "data": {"a": 3}, "reason": None, "at": None},
    description='последний ключ можно записать поверх словаря',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": 5, "z": {"y": 1}}, ["a", "b"], 1),
    expected={"status": "rejected", "data": {"a": 5, "z": {"y": 1}}, "reason": "not_a_dict", "at": "a"},
    description='при отказе соседние ветки не тронуты',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"lang": "ru"}, "b": {"lang": "ru"}}, ["a", "lang"], "en"),
    expected={"status": "done", "data": {"a": {"lang": "en"}, "b": {"lang": "ru"}}, "reason": None, "at": None},
    description='общая ветка у двух ключей: меняется только выбранный',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, "b"), (0, "a")),),
)

@case(
    args=({"a": {"b": {"c": 1}}}, ["a", "b", "c", "d"], 0),
    expected={"status": "rejected", "data": {"a": {"b": {"c": 1}}}, "reason": "not_a_dict", "at": "a.b.c"},
    description='отказ на третьем шаге',
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

def task_ns11_set_path(data, path, value):
    ...
