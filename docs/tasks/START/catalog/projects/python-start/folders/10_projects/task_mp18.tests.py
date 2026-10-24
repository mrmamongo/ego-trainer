from ego.testing import case

@case(
    args=('101', 2),
    expected=5,
    description='двоичное',
    level="smoke",
)

@case(
    args=('FF', 16),
    expected=255,
    description='шестнадцатеричное',
    level="smoke",
)

@case(
    args=('377', 8),
    expected=255,
    description='восьмеричное',
    level="smoke",
)

@case(
    args=('0', 2),
    expected=0,
    description='ноль',
    level="full",
)

@case(
    args=('10', 16),
    expected=16,
    description='ровно основание',
    level="full",
)

@case(
    args=('1010', 2),
    expected=10,
    description='десять',
    level="full",
)

@case(
    args=('FFF', 16),
    expected=4095,
    description='три F',
    level="full",
)

@case(
    args=('100', 10),
    expected=100,
    description='десятичное',
    level="full",
)

@case(
    args=('21', 3),
    expected=7,
    description='троичное',
    level="full",
)

@case(
    args=('0010', 2),
    expected=2,
    description='ведущие нули',
    level="full",
)

@case(
    args=('2B', 12),
    expected=35,
    description='двенадцатеричное',
    level="full",
)

def task_mp18_from_base(text, base):
    ...
