from ego.testing import case


@case(
    args=(5, False),
    expected=250,
    description='обычная поездка',
    level="smoke",
)

@case(
    args=(5, True),
    expected=500,
    description='ночная поездка',
    level="smoke",
)

@case(
    args=(0, False),
    expected=150,
    description='нулевая поездка — минимальная плата',
    level="smoke",
)

@case(
    args=(1, False),
    expected=150,
    description='130 поднимается до 150',
    level="full",
)

@case(
    args=(2, False),
    expected=160,
    description='чуть выше минимума',
    level="full",
)

@case(
    args=(0, True),
    expected=200,
    description='ночью 100 удваивается до 200',
    level="full",
)

@case(
    args=(1, True),
    expected=260,
    description='ночью 130 удваивается',
    level="full",
)

@case(
    args=(10, False),
    expected=400,
    description='дальняя поездка',
    level="full",
)
def task_fn19_taxi_fare(km, is_night):
    ...
