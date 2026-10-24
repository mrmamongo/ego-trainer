from ego.testing import case

@case(
    args=([3, -2, 5],),
    expected=1,
    description='отрицательное в середине',
    level="smoke",
)

@case(
    args=([-1, 2],),
    expected=0,
    description='отрицательное первым: индекс 0',
    level="smoke",
)

@case(
    args=([1, 2, 3],),
    expected=-1,
    description='отрицательных нет',
    level="smoke",
)

@case(
    args=([],),
    expected=-1,
    description='пустой список',
    level="full",
)

@case(
    args=([4, 5, -6, -7],),
    expected=2,
    description='берётся первое из двух отрицательных',
    level="full",
)

@case(
    args=([0, 0, -1],),
    expected=2,
    description='ноль не считается отрицательным',
    level="full",
)

@case(
    args=([0, -1],),
    expected=1,
    description='ноль, потом отрицательное',
    level="full",
)

def task_fd09_first_negative(nums):
    ...
