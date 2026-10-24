from ego.testing import case

@case(
    args=([6, 5, 4, 1], 10),
    expected=[5, 4, 1],
    description='с конца: 1, 4, 5',
    level="smoke",
)

@case(
    args=([1, 9, 2, 8], 10),
    expected=[2, 8],
    description='девятка и единица не влезли',
    level="smoke",
)

@case(
    args=([10, 1, 1, 1], 3),
    expected=[1, 1, 1],
    description='дорогая в начале пропущена',
    level="smoke",
)

@case(
    args=([], 5),
    expected=[],
    description='пустой список',
    level="full",
)

@case(
    args=([20, 30], 10),
    expected=[],
    description='ничего не влезло',
    level="full",
)

@case(
    args=([3], 10),
    expected=[3],
    description='одна цена',
    level="full",
)

@case(
    args=([5, 5, 5], 10),
    expected=[5, 5],
    description='две из трёх',
    level="full",
)

@case(
    args=([2, 7, 3], 10),
    expected=[7, 3],
    description='порядок результата как в списке',
    level="full",
)

@case(
    args=([4, 8, 3, 2], 10),
    expected=[4, 3, 2],
    description='с конца: 2, 3, 4',
    level="full",
)
def task_bk21_take_newest_skip_too_big(prices, budget):
    ...
