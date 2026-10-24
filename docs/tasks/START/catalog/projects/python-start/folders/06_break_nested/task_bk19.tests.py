from ego.testing import case, rules

@case(
    args=([4, 3, 5, 1], 10),
    expected=[4, 3],
    description='стоп на третьей цене',
    level="smoke",
)

@case(
    args=([5, 5, 5], 10),
    expected=[5, 5],
    description='две из трёх',
    level="smoke",
)

@case(
    args=([3, 3], 10),
    expected=[3, 3],
    description='все влезли',
    level="smoke",
)

@case(
    args=([20, 1], 10),
    expected=[],
    description='первая не влезла',
    level="full",
)

@case(
    args=([], 5),
    expected=[],
    description='пустой список',
    level="full",
)

@case(
    args=([4, 6], 10),
    expected=[4, 6],
    description='ровно по границе',
    level="full",
)

@case(
    args=([2, 9, 1, 1], 10),
    expected=[2],
    description='после стопа маленькие не берём',
    level="full",
)

@case(
    args=([3, 1], 0),
    expected=[],
    description='нулевой бюджет',
    level="full",
)


@rules(forbid_names=["sum", "max", "min", "sorted"])

def task_bk19_take_while_fits(prices, budget):
    ...
