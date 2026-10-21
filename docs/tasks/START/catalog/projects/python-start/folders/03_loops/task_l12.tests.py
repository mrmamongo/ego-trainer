from ego.testing import case

@case(
    args=([1, 2, 3],),
    expected=[2, 4, 6],
    description='простой список',
    level="smoke",
)

@case(
    args=([0],),
    expected=[0],
    description='ноль остаётся нулём',
    level="smoke",
)

@case(
    args=([-1, 5],),
    expected=[-2, 10],
    description='отрицательное и положительное',
    level="smoke",
)

@case(
    args=([],),
    expected=[],
    description='пустой список',
    level="full",
)

@case(
    args=([10, 20, 30, 40],),
    expected=[20, 40, 60, 80],
    description='четыре числа',
    level="full",
)

@case(
    args=([7, 7],),
    expected=[14, 14],
    description='повторяющиеся числа',
    level="full",
)
def task_l12_doubled(numbers):
    ...
