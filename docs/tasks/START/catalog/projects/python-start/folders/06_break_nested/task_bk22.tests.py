from ego.testing import case, rules

@case(
    args=([5, 4, 3, 2], 10),
    expected=[5, 3, 2],
    description='обязательная вытесняет четвёрку',
    level="smoke",
)

@case(
    args=([6, 1, 1, 5], 10),
    expected=[6, 1, 1],
    description='пятёрка не влезла',
    level="smoke",
)

@case(
    args=([11, 1], 10),
    expected=[],
    description='обязательная не влезает',
    level="smoke",
)

@case(
    args=([10, 1], 10),
    expected=[10],
    description='обязательная съела весь бюджет',
    level="full",
)

@case(
    args=([3], 10),
    expected=[3],
    description='одна цена',
    level="full",
)

@case(
    args=([], 10),
    expected=[],
    description='пустой список',
    level="full",
)

@case(
    args=([2, 9, 1, 8], 10),
    expected=[2, 8],
    description='с конца влезла только восьмёрка',
    level="full",
)

@case(
    args=([4, 6, 1, 5], 10),
    expected=[4, 1, 5],
    description='шестёрка пропущена',
    level="full",
)

@case(
    args=([4, 1, 2, 3], 10),
    expected=[4, 1, 2, 3],
    description='влезли все',
    level="full",
)


@rules(forbid_names=["sum", "max", "min", "sorted"])

def task_bk22_take_with_required_first(prices, budget):
    ...
