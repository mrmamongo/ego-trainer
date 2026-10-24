from ego.testing import case

@case(
    args=([1, 2, 3, 4],),
    expected=2,
    description='две чётных из четырёх',
    level="smoke",
)

@case(
    args=([2, 4, 6],),
    expected=3,
    description='все чётные',
    level="smoke",
)

@case(
    args=([1, 3],),
    expected=0,
    description='ни одного чётного',
    level="smoke",
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=([0, -2, -3],),
    expected=2,
    description='ноль и отрицательные',
    level="full",
)

@case(
    args=([7],),
    expected=0,
    description='один нечётный',
    level="full",
)

def task_fd02_count_even(nums):
    ...
