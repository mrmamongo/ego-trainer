from ego.testing import case, rules

@case(
    args=([4, 8, 3, 2], 10),
    expected=[4, 3, 2],
    description='пропуск одной цены',
    level="smoke",
)

@case(
    args=([20, 1], 10),
    expected=[1],
    description='первая не влезла, вторая влезла',
    level="smoke",
)

@case(
    args=([3, 3], 10),
    expected=[3, 3],
    description='все влезли',
    level="smoke",
)

@case(
    args=([], 5),
    expected=[],
    description='пустой список',
    level="full",
)

@case(
    args=([9, 2, 2, 1], 10),
    expected=[9, 1],
    description='несколько пропусков подряд',
    level="full",
)

@case(
    args=([6, 5, 4, 1], 10),
    expected=[6, 4],
    description='ровно по границе',
    level="full",
)

@case(
    args=([11, 12], 10),
    expected=[],
    description='ничего не влезло',
    level="full",
)

@case(
    args=([5, 5, 5], 10),
    expected=[5, 5],
    description='третья не влезла',
    level="full",
)

@case(
    args=([1, 1, 1], 2),
    expected=[1, 1],
    description='мелкие, лимит двух',
    level="full",
)


@rules(forbid_names=["sum", "max", "min", "sorted"])

def task_bk20_take_skip_too_big(prices, budget):
    ...
