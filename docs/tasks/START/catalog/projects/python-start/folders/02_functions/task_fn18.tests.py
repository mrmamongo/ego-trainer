from ego.testing import case


@case(
    args=(1, 1, 2, 3),
    expected=True,
    description='вправо на 1, вверх на 2',
    level="smoke",
)

@case(
    args=(1, 1, 3, 2),
    expected=True,
    description='вправо на 2, вверх на 1',
    level="smoke",
)

@case(
    args=(1, 1, 2, 2),
    expected=False,
    description='соседняя по диагонали — не ход коня',
    level="smoke",
)

@case(
    args=(4, 4, 3, 2),
    expected=True,
    description='влево на 1, вниз на 2',
    level="full",
)

@case(
    args=(4, 4, 6, 3),
    expected=True,
    description='вправо на 2, вниз на 1',
    level="full",
)

@case(
    args=(4, 4, 4, 4),
    expected=False,
    description='остался на месте',
    level="full",
)

@case(
    args=(1, 1, 3, 3),
    expected=False,
    description='разницы 2 и 2',
    level="full",
)

@case(
    args=(5, 5, 5, 7),
    expected=False,
    description='только по вертикали',
    level="full",
)
def task_fn18_knight_move(x1, y1, x2, y2):
    ...
