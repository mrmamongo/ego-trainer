from ego.testing import case

@case(
    args=(1, 10),
    expected=30,
    description='2 + 4 + 6 + 8 + 10',
    level='smoke',
)

@case(
    args=(4, 9),
    expected=18,
    description='4 + 6 + 8',
    level='smoke',
)

@case(
    args=(2, 2),
    expected=2,
    description='одно чётное число',
    level='smoke',
)

@case(
    args=(3, 3),
    expected=0,
    description='одно нечётное число',
    level='full',
)

@case(
    args=(1, 1),
    expected=0,
    description='единица',
    level='full',
)

@case(
    args=(0, 0),
    expected=0,
    description='ноль',
    level='full',
)

@case(
    args=(-4, 3),
    expected=-4,
    description='отрицательные тоже считаются: -4 - 2 + 0 + 2',
    level='full',
)

@case(
    args=(1, 100),
    expected=2550,
    description='до сотни',
    level='full',
)
def task_r08_sum_even(a, b):
    ...
