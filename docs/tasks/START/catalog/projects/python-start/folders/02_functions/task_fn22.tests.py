from ego.testing import case


@case(
    args=(3, 4),
    expected=1,
    description='первая четверть',
    level="smoke",
)

@case(
    args=(-3, 4),
    expected=2,
    description='вторая четверть',
    level="smoke",
)

@case(
    args=(-3, -4),
    expected=3,
    description='третья четверть',
    level="smoke",
)

@case(
    args=(3, -4),
    expected=4,
    description='четвёртая четверть',
    level="smoke",
)

@case(
    args=(0, 5),
    expected=0,
    description='на оси y',
    level="full",
)

@case(
    args=(5, 0),
    expected=0,
    description='на оси x',
    level="full",
)

@case(
    args=(0, 0),
    expected=0,
    description='начало координат',
    level="full",
)

@case(
    args=(-1, 0),
    expected=0,
    description='отрицательная ось x',
    level="full",
)
def task_fn22_quadrant(x, y):
    ...
