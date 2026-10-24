from ego.testing import case, rules

@case(
    args=([1, 2, 3],),
    expected=6,
    description='простой список',
    level="smoke",
)

@case(
    args=([10],),
    expected=10,
    description='один элемент',
    level="smoke",
)

@case(
    args=([],),
    expected=0,
    description='пустой список — начальное значение',
    level="smoke",
)

@case(
    args=([-5, 5],),
    expected=0,
    description='числа гасят друг друга',
    level="full",
)

@case(
    args=([-1, -2],),
    expected=-3,
    description='только отрицательные',
    level="full",
)

@case(
    args=([100, 200, 300, 400],),
    expected=1000,
    description='несколько больших чисел',
    level="full",
)


@rules(forbid_names=["sum"])

def task_l03_sum(numbers):
    ...
