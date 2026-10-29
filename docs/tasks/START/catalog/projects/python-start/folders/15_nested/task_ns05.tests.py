from ego.testing import case, rules

@case(
    args=([1, [2, [3]]],),
    expected=3,
    description='три уровня',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([1, 2, 3],),
    expected=1,
    description='плоский список',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([1, [2]],),
    expected=2,
    description='два уровня',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([],),
    expected=1,
    description='пустой список имеет глубину 1',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([[[]]],),
    expected=3,
    description='пустой список в глубине',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([[], [[]]],),
    expected=3,
    description='ветки разной глубины',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([[1], [2, [3]], 4],),
    expected=3,
    description='самая глубокая ветка не первая',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([[[[[["x"]]]]], [1]],),
    expected=6,
    description='глубокая вложенность',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)


@rules(
    forbid_names=["max", "sorted"],
    messages={
        "max": "Встроенную max использовать нельзя: запоминай лучшее через if",
        "sorted": "Встроенную sorted использовать нельзя: запоминай лучшее через if",
    },
)

def task_ns05_depth(items):
    ...
