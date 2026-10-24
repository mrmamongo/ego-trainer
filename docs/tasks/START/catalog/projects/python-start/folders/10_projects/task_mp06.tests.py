from ego.testing import case

@case(
    args=('a', 3),
    expected='d',
    description='обычная буква',
    level="smoke",
)

@case(
    args=('x', 3),
    expected='a',
    description='переход через z',
    level="smoke",
)

@case(
    args=('A', 3),
    expected='A',
    description='заглавная не трогается',
    level="smoke",
)

@case(
    args=('5', 2),
    expected='5',
    description='цифра',
    level="full",
)

@case(
    args=(' ', 1),
    expected=' ',
    description='пробел',
    level="full",
)

@case(
    args=('z', 1),
    expected='a',
    description='последняя буква',
    level="full",
)

@case(
    args=('b', -1),
    expected='a',
    description='сдвиг назад',
    level="full",
)

@case(
    args=('a', -1),
    expected='z',
    description='назад через начало',
    level="full",
)

@case(
    args=('c', 26),
    expected='c',
    description='полный круг',
    level="full",
)

@case(
    args=('c', 29),
    expected='f',
    description='больше круга',
    level="full",
)

@case(
    args=('я', 3),
    expected='я',
    description='русская буква не трогается',
    level="full",
)

@case(
    args=('!', 5),
    expected='!',
    description='знак',
    level="full",
)

def task_mp06_shift_letter(ch, k):
    ...
