from ego.testing import case

@case(
    args=('Khoor, Zruog!', 3),
    expected='Hello, World!',
    description='расшифровка фразы',
    level="smoke",
)

@case(
    args=('bcd', 1),
    expected='abc',
    description='сдвиг на единицу',
    level="smoke",
)

@case(
    args=('abc', 3),
    expected='xyz',
    description='переход через начало',
    level="smoke",
)

@case(
    args=('', 4),
    expected='',
    description='пустая строка',
    level="full",
)

@case(
    args=('Aa', 1),
    expected='Zz',
    description='заглавная a',
    level="full",
)

@case(
    args=('abc', 0),
    expected='abc',
    description='нулевой ключ',
    level="full",
)

@case(
    args=('def', -3),
    expected='ghi',
    description='отрицательный ключ',
    level="full",
)

@case(
    args=('Dwwdfn', 3),
    expected='Attack',
    description='регистр',
    level="full",
)

@case(
    args=('Dwwdfn', 29),
    expected='Attack',
    description='ключ больше круга',
    level="full",
)

@case(
    args=('a1 b2!', 1),
    expected='z1 a2!',
    description='цифры и знаки',
    level="full",
)

def task_mp08_decode(text, k):
    ...
