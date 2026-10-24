from ego.testing import case

@case(
    args=(6,),
    expected='110',
    description='шесть',
    level="smoke",
)

@case(
    args=(5,),
    expected='101',
    description='пять',
    level="smoke",
)

@case(
    args=(0,),
    expected='0',
    description='ноль',
    level="smoke",
)

@case(
    args=(1,),
    expected='1',
    description='единица',
    level="full",
)

@case(
    args=(2,),
    expected='10',
    description='степень двойки',
    level="full",
)

@case(
    args=(10,),
    expected='1010',
    description='десять',
    level="full",
)

@case(
    args=(255,),
    expected='11111111',
    description='все единицы',
    level="full",
)

@case(
    args=(256,),
    expected='100000000',
    description='256',
    level="full",
)

@case(
    args=(1023,),
    expected='1111111111',
    description='1023',
    level="full",
)

@case(
    args=(12345,),
    expected='11000000111001',
    description='большое число',
    level="full",
)

def task_mp16_to_binary(n):
    ...
