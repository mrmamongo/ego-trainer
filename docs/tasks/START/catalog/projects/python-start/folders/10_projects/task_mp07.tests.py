from ego.testing import case

@case(
    args=('abc', 1),
    expected='bcd',
    description='простое слово',
    level="smoke",
)

@case(
    args=('Hello, World!', 3),
    expected='Khoor, Zruog!',
    description='регистр и знаки',
    level="smoke",
)

@case(
    args=('xyz', 3),
    expected='abc',
    description='переход через z',
    level="smoke",
)

@case(
    args=('', 5),
    expected='',
    description='пустая строка',
    level="full",
)

@case(
    args=('ABC', 1),
    expected='BCD',
    description='только заглавные',
    level="full",
)

@case(
    args=('Zz', 1),
    expected='Aa',
    description='z и Z',
    level="full",
)

@case(
    args=('a1 b2', 1),
    expected='b1 c2',
    description='цифры и пробел',
    level="full",
)

@case(
    args=('Привет, мир', 5),
    expected='Привет, мир',
    description='русский текст не меняется',
    level="full",
)

@case(
    args=('Khoor', -3),
    expected='Hello',
    description='отрицательный сдвиг',
    level="full",
)

@case(
    args=('abc', 0),
    expected='abc',
    description='нулевой сдвиг',
    level="full",
)

@case(
    args=('abc', 29),
    expected='def',
    description='сдвиг больше круга',
    level="full",
)

def task_mp07_encode(text, k):
    ...
