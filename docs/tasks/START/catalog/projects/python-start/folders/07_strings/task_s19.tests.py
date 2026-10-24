from ego.testing import case

@case(
    args=(5,),
    expected="5.00 ₽",
    description="целое число",
    level="smoke",
)

@case(
    args=(12.5,),
    expected="12.50 ₽",
    description="полтинник",
    level="smoke",
)

@case(
    args=(0,),
    expected="0.00 ₽",
    description="ноль",
    level="smoke",
)

@case(
    args=(1234.567,),
    expected="1234.57 ₽",
    description="округление вверх",
    level="full",
)

@case(
    args=(99.999,),
    expected="100.00 ₽",
    description="округление до круглого",
    level="full",
)

@case(
    args=(0.5,),
    expected="0.50 ₽",
    description="меньше единицы",
    level="full",
)

@case(
    args=(1000000,),
    expected="1000000.00 ₽",
    description="большое число",
    level="full",
)
def task_s19_format_price(amount):
    ...
