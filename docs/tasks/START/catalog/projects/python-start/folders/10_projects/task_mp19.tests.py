from ego.testing import case

@case(
    args=(-5, 2),
    expected='-101',
    description='минус пять',
    level="smoke",
)

@case(
    args=(-255, 16),
    expected='-FF',
    description='минус 255',
    level="smoke",
)

@case(
    args=(5, 2),
    expected='101',
    description='положительное как раньше',
    level="smoke",
)

@case(
    args=(0, 2),
    expected='0',
    description='ноль',
    level="full",
)

@case(
    args=(-1, 10),
    expected='-1',
    description='минус один',
    level="full",
)

@case(
    args=(-16, 16),
    expected='-10',
    description='минус основание',
    level="full",
)

@case(
    args=(255, 16),
    expected='FF',
    description='положительное шестнадцатеричное',
    level="full",
)

@case(
    args=(-8, 8),
    expected='-10',
    description='восьмеричное',
    level="full",
)

@case(
    args=(-100, 10),
    expected='-100',
    description='десятичное',
    level="full",
)

@case(
    args=(0, 16),
    expected='0',
    description='ноль в шестнадцатеричной',
    level="full",
)

@case(
    args=(-35, 12),
    expected='-2B',
    description='двенадцатеричное',
    level="full",
)

def task_mp19_to_base(n, base):
    ...
