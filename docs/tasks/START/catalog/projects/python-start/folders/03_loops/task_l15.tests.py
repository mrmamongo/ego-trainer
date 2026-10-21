from ego.testing import case

@case(
    args=([1, -2, 3],),
    expected=True,
    description='отрицательное посередине',
    level="smoke",
)

@case(
    args=([1, 2, 3],),
    expected=False,
    description='отрицательных нет',
    level="smoke",
)

@case(
    args=([-5],),
    expected=True,
    description='единственное отрицательное',
    level="smoke",
)

@case(
    args=([],),
    expected=False,
    description='пустой список',
    level="full",
)

@case(
    args=([0, 0],),
    expected=False,
    description='ноль не отрицательный',
    level="full",
)

@case(
    args=([4, 5, -1],),
    expected=True,
    description='отрицательное в конце',
    level="full",
)

@case(
    args=([-1, -2, -3],),
    expected=True,
    description='все отрицательные',
    level="full",
)
def task_l15_has_negative(numbers):
    ...
