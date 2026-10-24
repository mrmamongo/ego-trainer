from ego.testing import case, rules

@case(
    args=([1, 2, 3],),
    expected=2.0,
    description='целое среднее',
    level="smoke",
)

@case(
    args=([10],),
    expected=10.0,
    description='один элемент',
    level="smoke",
)

@case(
    args=([1, 2],),
    expected=1.5,
    description='дробное среднее',
    level="smoke",
)

@case(
    args=([],),
    expected=0.0,
    description='пустой список',
    level="full",
)

@case(
    args=([0, 0, 0],),
    expected=0.0,
    description='одни нули',
    level="full",
)

@case(
    args=([1, 2, 3, 4],),
    expected=2.5,
    description='четыре числа',
    level="full",
)

@case(
    args=([-2, 2],),
    expected=0.0,
    description='числа гасят друг друга',
    level="full",
)

@case(
    args=([5, 10],),
    expected=7.5,
    description='дробное среднее двух чисел',
    level="full",
)


@rules(forbid_names=["sum", "len"])

def task_l21_average(numbers):
    ...
