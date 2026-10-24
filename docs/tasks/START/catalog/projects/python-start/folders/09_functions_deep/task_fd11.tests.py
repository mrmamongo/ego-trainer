from ego.testing import case

@case(
    args=([1, 2, 3], 10),
    expected=[1, 2, 3],
    description='старый случай: всё помещается',
    level="smoke",
)

@case(
    args=([4, 8, 3, 2], 10),
    expected=[4, 3, 2],
    description='8 не влезло, дальше берём',
    level="smoke",
)

@case(
    args=([20, 3], 10),
    expected=[3],
    description='первая цена слишком большая',
    level="smoke",
)

@case(
    args=([5, 5, 5], 10),
    expected=[5, 5],
    description='третья цена не влезает',
    level="full",
)

@case(
    args=([], 5),
    expected=[],
    description='пустой список',
    level="full",
)

@case(
    args=([3, 3], 0),
    expected=[],
    description='бюджет нулевой',
    level="full",
)

@case(
    args=([6, 5, 4], 10),
    expected=[6, 4],
    description='5 пропущена, 4 попадает ровно в бюджет',
    level="full",
)

@case(
    args=([10], 10),
    expected=[10],
    description='цена ровно равна бюджету',
    level="full",
)

def task_fd11_take_within_budget(items, budget):
    ...
