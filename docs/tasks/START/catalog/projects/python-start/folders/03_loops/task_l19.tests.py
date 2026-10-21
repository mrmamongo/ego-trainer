from ego.testing import case

@case(
    args=([3, 9, 2],),
    expected=9,
    description='максимум посередине',
    level="smoke",
)

@case(
    args=([5],),
    expected=5,
    description='один элемент',
    level="smoke",
)

@case(
    args=([1, 2, 3],),
    expected=3,
    description='максимум в конце',
    level="smoke",
)

@case(
    args=([-5, -2, -9],),
    expected=-2,
    description='все отрицательные',
    level="full",
)

@case(
    args=([7, 7, 7],),
    expected=7,
    description='все равны',
    level="full",
)

@case(
    args=([10, 4, 10, 1],),
    expected=10,
    description='максимум встречается дважды',
    level="full",
)

@case(
    args=([9, 1, 2],),
    expected=9,
    description='максимум в начале',
    level="full",
)
def task_l19_max_value(numbers):
    ...
