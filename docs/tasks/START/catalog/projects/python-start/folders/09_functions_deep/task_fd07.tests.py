from ego.testing import case

@case(
    args=(100,),
    expected=120,
    description='старый вызов с одним аргументом',
    level="smoke",
)

@case(
    args=(50,),
    expected=60,
    description='ещё один старый вызов',
    level="smoke",
)

@case(
    args=(100, 10),
    expected=110,
    description='ставка 10',
    level="smoke",
)

@case(
    args=(200, 0),
    expected=200,
    description='нулевая ставка',
    level="smoke",
)

@case(
    args=(0,),
    expected=0,
    description='нулевая цена по умолчанию',
    level="full",
)

@case(
    args=(99,),
    expected=118,
    description='округление вниз по умолчанию',
    level="full",
)

@case(
    args=(150, 15),
    expected=172,
    description='ставка 15 и округление',
    level="full",
)

@case(
    args=(80, 25),
    expected=100,
    description='ставка 25',
    level="full",
)

def task_fd07_price_with_vat(price, rate=20):
    ...
