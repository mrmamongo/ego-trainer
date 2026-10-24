from ego.testing import case

@case(
    args=("1290",),
    expected=1548,
    description='обычная цена',
    level="smoke",
)

@case(
    args=("10",),
    expected=12,
    description='маленькая цена',
    level="smoke",
)

@case(
    args=("0",),
    expected=0,
    description='начинается с нуля',
    level="smoke",
)

@case(
    args=("100",),
    expected=120,
    description='круглая сотня',
    level="full",
)

@case(
    args=("7",),
    expected=8,
    description='некруглое число',
    level="full",
)

@case(
    args=("12345",),
    expected=14814,
    description='большая цена',
    level="full",
)
def task_n04_parse_price(text):
    ...
