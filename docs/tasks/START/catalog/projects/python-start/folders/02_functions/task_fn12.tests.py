from ego.testing import case


@case(
    args=(1000, True),
    expected=900,
    description='участник, скидка 10%',
    level="smoke",
)

@case(
    args=(1000, False),
    expected=1000,
    description='не участник, без скидки',
    level="smoke",
)

@case(
    args=(6000, False),
    expected=5500,
    description='не участник, больше 5000',
    level="smoke",
)

@case(
    args=(6000, True),
    expected=4900,
    description='участник: 5400, затем ещё минус 500',
    level="full",
)

@case(
    args=(5000, False),
    expected=5000,
    description='ровно 5000 — вторая скидка не нужна',
    level="full",
)

@case(
    args=(5500, True),
    expected=4950,
    description='после скидки 4950 — не больше 5000',
    level="full",
)

@case(
    args=(5001, False),
    expected=4501,
    description='5001 — уже больше 5000',
    level="full",
)

@case(
    args=(5555, True),
    expected=5000,
    description='после скидки ровно 5000',
    level="full",
)

@case(
    args=(5556, True),
    expected=4501,
    description='после скидки 5001',
    level="full",
)

@case(
    args=(0, True),
    expected=0,
    description='нулевая цена',
    level="full",
)

@case(
    args=(9, True),
    expected=9,
    description='скидка округляется вниз до нуля',
    level="full",
)
def task_fn12_final_price(price, is_member):
    ...
