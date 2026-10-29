from ego.testing import case, rules

@case(
    args=({"a": [1, 2], "b": {"c": 3}},),
    expected={"a": [1, 2], "b": {"c": 3}},
    description='словарь со списком и словарём',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, [2, [3]]],),
    expected=[1, [2, [3]]],
    description='вложенные списки',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{"id": 1, "tags": ["a"]}, {"id": 2, "tags": []}],),
    expected=[{"id": 1, "tags": ["a"]}, {"id": 2, "tags": []}],
    description='список словарей',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=(5,),
    expected=5,
    description='число',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=("text",),
    expected="text",
    description='строка',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=(None,),
    expected=None,
    description='None',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({},),
    expected={},
    description='пустой словарь',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([],),
    expected=[],
    description='пустой список',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"a": {"b": {"c": {"d": [1, {"e": None}]}}}, "f": [[], {}], "g": False},),
    expected={"a": {"b": {"c": {"d": [1, {"e": None}]}}}, "f": [[], {}], "g": False},
    description='глубокая вложенность и пустые контейнеры',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    hide_expected=True,
)

@case(
    args=({"a": [1, 2], "b": [1, 2]},),
    expected={"a": [1, 2], "b": [1, 2]},
    description='общий список у двух ключей',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, "b"), (0, "a")),),
    hide_expected=True,
)


@rules(
    forbid_imports=["copy", "json"],
    forbid_names=["deepcopy"],
    messages={
        "copy": "Модуль copy использовать нельзя: копию собирает рекурсия",
        "json": "Модуль json использовать нельзя: копию собирает рекурсия",
        "deepcopy": "deepcopy использовать нельзя: копию собирает рекурсия",
    },
)

def task_ns10_deep_copy(data):
    ...
