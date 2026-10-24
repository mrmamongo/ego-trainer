from ego.testing import case, rules

@case(
    args=('привет', 1),
    expected='рсйгёу',
    description='русское слово',
    level="smoke",
)

@case(
    args=('Hello', 3),
    expected='Khoor',
    description='латиница как раньше',
    level="smoke",
)

@case(
    args=('Яблоко', 1),
    expected='Авмплп',
    description='заглавная и переход через я',
    level="smoke",
)

@case(
    args=('', 5),
    expected='',
    description='пустая строка',
    level="full",
)

@case(
    args=('я', 1),
    expected='а',
    description='последняя буква',
    level="full",
)

@case(
    args=('ёж', 1),
    expected='жз',
    description='буква ё',
    level="full",
)

@case(
    args=('Привет, World!', 2),
    expected='Сткджф, Yqtnf!',
    description='смешанный текст',
    level="full",
)

@case(
    args=('мир', -1),
    expected='лзп',
    description='сдвиг назад',
    level="full",
)

@case(
    args=('абв', 33),
    expected='абв',
    description='полный круг русского алфавита',
    level="full",
)

@case(
    args=('абв', 34),
    expected='бвг',
    description='больше круга',
    level="full",
)

@case(
    args=('Ёлка 2024', 3),
    expected='Ионг 2024',
    description='цифры и ё',
    level="full",
)

@case(
    args=('xyz abc', 3),
    expected='abc def',
    description='латиница после правки',
    level="full",
)


@rules(forbid_names=["ord", "chr"], forbid_methods=["translate", "maketrans"])

def task_mp09_encode(text, k):
    ...
