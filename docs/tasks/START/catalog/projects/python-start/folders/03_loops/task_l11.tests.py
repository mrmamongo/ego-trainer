from ego.testing import case

@case(
    args=([50, 70, 90], 60),
    expected=[70, 90],
    description='часть прошла',
    level="smoke",
)

@case(
    args=([80, 60, 59], 60),
    expected=[80, 60],
    description='граница включается',
    level="smoke",
)

@case(
    args=([10, 20], 50),
    expected=[],
    description='никто не прошёл',
    level="smoke",
)

@case(
    args=([], 5),
    expected=[],
    description='пустой список',
    level="full",
)

@case(
    args=([5, 5, 5], 5),
    expected=[5, 5, 5],
    description='все ровно на границе',
    level="full",
)

@case(
    args=([90, 10, 70, 30, 60], 50),
    expected=[90, 70, 60],
    description='порядок сохраняется',
    level="full",
)
def task_l11_passed(scores, threshold):
    ...
