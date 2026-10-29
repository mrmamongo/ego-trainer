from ego.testing import case, rules

@case(
    args=([1, [2, [3]], 4],),
    expected=[1, 2, 3, 4],
    description='порядок сохраняется',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[1, 2], [3, [4, 5]]],),
    expected=[1, 2, 3, 4, 5],
    description='списки рядом и глубже',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3],),
    expected=[1, 2, 3],
    description='уже плоский список',
    level="smoke",
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
    args=([[], [[]]],),
    expected=[],
    description='только пустые списки',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=(["a", ["b", ["c"]], "d"],),
    expected=["a", "b", "c", "d"],
    description='строки',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[[[7]]], 8, [[9]]],),
    expected=[7, 8, 9],
    description='глубокие скобки',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    hide_expected=True,
)

@case(
    args=([1, [], [None, [0]], False],),
    expected=[1, None, 0, False],
    description='None, ноль и False тоже значения',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    hide_expected=True,
)


@rules(
    forbid_names=["sum"],
    messages={"sum": "Встроенную sum использовать нельзя: список собирает рекурсия"},
)

def task_ns04_flatten(items):
    ...
