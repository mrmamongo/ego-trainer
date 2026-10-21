from ego.testing import case

@case(
    args=([60, 70, 80], 60),
    expected=True,
    description='все прошли',
    level="smoke",
)

@case(
    args=([60, 59, 80], 60),
    expected=False,
    description='один не прошёл',
    level="smoke",
)

@case(
    args=([10, 20], 50),
    expected=False,
    description='никто не прошёл',
    level="smoke",
)

@case(
    args=([], 50),
    expected=True,
    description='пустой список — нарушителей нет',
    level="full",
)

@case(
    args=([50], 50),
    expected=True,
    description='ровно на границе',
    level="full",
)

@case(
    args=([90, 80, 40], 50),
    expected=False,
    description='нарушитель в конце',
    level="full",
)

@case(
    args=([49], 50),
    expected=False,
    description='на единицу ниже порога',
    level="full",
)
def task_l16_all_passed(scores, threshold):
    ...
