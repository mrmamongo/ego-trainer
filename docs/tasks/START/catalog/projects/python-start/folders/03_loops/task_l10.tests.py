from ego.testing import case

@case(
    args=([1, 2, 3, 4],),
    expected=[2, 4],
    description='чётные и нечётные',
    level="smoke",
)

@case(
    args=([2, 4, 6],),
    expected=[2, 4, 6],
    description='все чётные',
    level="smoke",
)

@case(
    args=([1, 3, 5],),
    expected=[],
    description='ни одного чётного',
    level="smoke",
)

@case(
    args=([],),
    expected=[],
    description='пустой список',
    level="full",
)

@case(
    args=([0, -2, -3],),
    expected=[0, -2],
    description='ноль и отрицательные',
    level="full",
)

@case(
    args=([10, 7, 8, 9, 12],),
    expected=[10, 8, 12],
    description='порядок сохраняется',
    level="full",
)
def task_l10_evens(numbers):
    ...
