from ego.testing import case, rules

@case(
    args=([3, 1, 4, 1, 5],),
    expected=(1, 5),
    description='обычный список',
    level="smoke",
)

@case(
    args=([7],),
    expected=(7, 7),
    description='один элемент',
    level="smoke",
)

@case(
    args=([-2, -9, -4],),
    expected=(-9, -2),
    description='все отрицательные',
    level="smoke",
)

@case(
    args=([2, 2],),
    expected=(2, 2),
    description='два одинаковых',
    level="full",
)

@case(
    args=([0, 10, -10],),
    expected=(-10, 10),
    description='ноль между крайними',
    level="full",
)

@case(
    args=([5, 4, 3, 2, 1],),
    expected=(1, 5),
    description='список по убыванию',
    level="full",
)


@rules(forbid_names=["min", "max"])

def task_fd14_min_max(nums):
    ...
