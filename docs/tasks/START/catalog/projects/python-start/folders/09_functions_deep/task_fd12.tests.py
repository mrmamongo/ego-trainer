from ego.testing import case

@case(
    args=([4, 8, 3, 2], 10),
    expected=[4, 3, 2],
    description='старый случай: первая влезает, дорогая пропускается',
    level="smoke",
)

@case(
    args=([20, 3], 10),
    expected=[],
    description='первая цена не влезает: пусто',
    level="smoke",
)

@case(
    args=([12, 1], 10),
    expected=[],
    description='первая больше бюджета, остальные мелкие',
    level="smoke",
)

@case(
    args=([10], 10),
    expected=[10],
    description='первая цена ровно равна бюджету',
    level="full",
)

@case(
    args=([], 10),
    expected=[],
    description='пустой список',
    level="full",
)

@case(
    args=([5, 6, 5], 10),
    expected=[5, 5],
    description='пропуск в середине',
    level="full",
)

@case(
    args=([11, 1, 1], 10),
    expected=[],
    description='первая не влезает, дальше мелочь',
    level="full",
)

@case(
    args=([3, 20, 3], 10),
    expected=[3, 3],
    description='дорогая цена в середине',
    level="full",
)

@case(
    args=([1, 2, 3], 10),
    expected=[1, 2, 3],
    description='всё помещается',
    level="full",
)

def task_fd12_take_within_budget(items, budget):
    ...
