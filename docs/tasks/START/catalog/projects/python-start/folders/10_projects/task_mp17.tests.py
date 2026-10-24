from ego.testing import case

@case(
    args=(10, 2),
    expected='1010',
    description='двоичная',
    level="smoke",
)

@case(
    args=(255, 16),
    expected='FF',
    description='шестнадцатеричная',
    level="smoke",
)

@case(
    args=(255, 8),
    expected='377',
    description='восьмеричная',
    level="smoke",
)

@case(
    args=(0, 16),
    expected='0',
    description='ноль',
    level="full",
)

@case(
    args=(15, 16),
    expected='F',
    description='одна цифра-буква',
    level="full",
)

@case(
    args=(16, 16),
    expected='10',
    description='ровно основание',
    level="full",
)

@case(
    args=(100, 10),
    expected='100',
    description='десятичная',
    level="full",
)

@case(
    args=(4095, 16),
    expected='FFF',
    description='три F',
    level="full",
)

@case(
    args=(7, 3),
    expected='21',
    description='троичная',
    level="full",
)

@case(
    args=(35, 12),
    expected='2B',
    description='двенадцатеричная',
    level="full",
)

@case(
    args=(1, 2),
    expected='1',
    description='единица',
    level="full",
)

def task_mp17_to_base(n, base):
    ...
