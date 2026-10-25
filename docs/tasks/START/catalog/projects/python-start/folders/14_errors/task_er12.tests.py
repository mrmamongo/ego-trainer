from ego.testing import case

@case(
    args=(200, 25),
    expected=150,
    description='обычная скидка',
    level="smoke",
)

@case(
    args=(-5, 10),
    expected="bad_price",
    description='отрицательная цена',
    level="smoke",
)

@case(
    args=(100, 101),
    expected="percent_over_100",
    description='процент больше 100',
    level="smoke",
)

@case(
    args=(100, -1),
    expected="percent_below_0",
    description='отрицательный процент',
    level="smoke",
)

@case(
    args=(100, 0),
    expected=100,
    description='граница: нулевая скидка',
    level="full",
)

@case(
    args=(100, 100),
    expected=0,
    description='граница: скидка 100%',
    level="full",
)

@case(
    args=(0, 50),
    expected=0,
    description='нулевая цена допустима',
    level="full",
)

@case(
    args=(99, 50),
    expected=50,
    description='округление вниз скидки',
    level="full",
)

@case(
    args=(-5, 150),
    expected="bad_price",
    description='цена проверяется раньше процента',
    level="full",
    hide_expected=True,
)
def task_er12_final_price(price, percent):
    ...
