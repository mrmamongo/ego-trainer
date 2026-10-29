from ego.testing import case, rules

@case(
    args=([1, [2, [3]]],),
    expected=6,
    description='три уровня',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([1, 2, 3],),
    expected=6,
    description='плоский список',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([[4, 5], [6]],),
    expected=15,
    description='списки рядом',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([[], [[]]],),
    expected=0,
    description='только пустые списки',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([1, "a", [2, "b", ["3"]]],),
    expected=3,
    description='строки пропускаются',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([-1, [-2, [10]]],),
    expected=7,
    description='отрицательные числа',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([[[[[[1]]]]], 2],),
    expected=3,
    description='глубокая вложенность',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)


@rules(
    forbid_names=["sum"],
    messages={"sum": "Встроенную sum использовать нельзя: сумму собирает рекурсия"},
)

def task_ns03_nested_sum(items):
    ...
