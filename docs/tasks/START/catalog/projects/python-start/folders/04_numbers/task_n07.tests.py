from ego.testing import case

@case(
    args=([1, 2],),
    expected=1.5,
    description='дробное среднее',
    level="smoke",
)

@case(
    args=([1, 2, 3],),
    expected=2.0,
    description='ровно делится',
    level="smoke",
)

@case(
    args=([10, 20, 30],),
    expected=20.0,
    description='десятки',
    level="smoke",
)

@case(
    args=([],),
    expected=0.0,
    description='пустой список',
    level="full",
)

@case(
    args=([5],),
    expected=5.0,
    description='одно число',
    level="full",
)

@case(
    args=([-1, -2],),
    expected=-1.5,
    description='отрицательные',
    level="full",
)

@case(
    args=([1, 2, 4, 5],),
    expected=3.0,
    description='сумма 12 на четыре числа',
    level="full",
)
def task_n07_average(numbers):
    ...
