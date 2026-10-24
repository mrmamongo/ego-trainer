from ego.testing import case, rules

@case(
    args=([2, 4, 6],),
    expected=(3, 12, 4.0),
    description='обычный список',
    level="smoke",
    comparison="value",
)

@case(
    args=([5],),
    expected=(1, 5, 5.0),
    description='один элемент',
    level="smoke",
    comparison="value",
)

@case(
    args=([1, 2],),
    expected=(2, 3, 1.5),
    description='дробное среднее',
    level="smoke",
    comparison="value",
)

@case(
    args=([],),
    expected=(0, 0, 0),
    description='пустой список',
    level="full",
    comparison="value",
)

@case(
    args=([-2, 2],),
    expected=(2, 0, 0.0),
    description='сумма равна нулю',
    level="full",
    comparison="value",
)

@case(
    args=([10, 20, 30, 40],),
    expected=(4, 100, 25.0),
    description='четыре числа',
    level="full",
    comparison="value",
)


@rules(forbid_names=["len", "sum"])

def task_fd15_stats(nums):
    ...
