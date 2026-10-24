from ego.testing import case, rules

@case(
    args=('101', 2, 10),
    expected='5',
    description='двоичная в десятичную',
    level="smoke",
)

@case(
    args=('FF', 16, 2),
    expected='11111111',
    description='шестнадцатеричная в двоичную',
    level="smoke",
)

@case(
    args=('255', 10, 16),
    expected='FF',
    description='десятичная в шестнадцатеричную',
    level="smoke",
)

@case(
    args=('-FF', 16, 10),
    expected='-255',
    description='отрицательное',
    level="full",
)

@case(
    args=('0', 2, 16),
    expected='0',
    description='ноль',
    level="full",
)

@case(
    args=('377', 8, 16),
    expected='FF',
    description='восьмеричная в шестнадцатеричную',
    level="full",
)

@case(
    args=('-101', 2, 8),
    expected='-5',
    description='отрицательное двоичное',
    level="full",
)

@case(
    args=('1010', 2, 16),
    expected='A',
    description='одна цифра-буква',
    level="full",
)

@case(
    args=('10', 10, 10),
    expected='10',
    description='то же основание',
    level="full",
)

@case(
    args=('A', 16, 3),
    expected='101',
    description='в троичную',
    level="full",
)

@case(
    args=('-1', 10, 2),
    expected='-1',
    description='минус один',
    level="full",
)


@rules(forbid_names=["int", "bin", "oct", "hex", "format"])

def task_mp20_convert(text, base_from, base_to):
    ...
