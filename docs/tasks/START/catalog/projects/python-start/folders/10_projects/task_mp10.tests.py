from ego.testing import case

@case(
    args=('Khoor, Zruog!', 'World'),
    expected=3,
    description='латиница',
    level="smoke",
)

@case(
    args=('abc', 'abc'),
    expected=0,
    description='ключ ноль',
    level="smoke",
)

@case(
    args=('abc', 'zzz'),
    expected=-1,
    description='слова нет ни при каком ключе',
    level="smoke",
)

@case(
    args=('Khoor', 'Hello'),
    expected=3,
    description='одно слово',
    level="full",
)

@case(
    args=('dwwdfn dw gdzq', 'attack'),
    expected=3,
    description='слово внутри фразы',
    level="full",
)

@case(
    args=('Dwwdfn dw gdzq', 'attack'),
    expected=-1,
    description='регистр важен',
    level="full",
)

@case(
    args=('Фхнжйч, снх!', 'мир'),
    expected=5,
    description='русский текст',
    level="full",
)

@case(
    args=('йён', 'мир'),
    expected=30,
    description='большой русский ключ',
    level="full",
)

@case(
    args=('khoor', 'hello'),
    expected=3,
    description='ключ больше круга, берём наименьший',
    level="full",
)

@case(
    args=('', 'a'),
    expected=-1,
    description='пустая шифровка',
    level="full",
)

@case(
    args=('Zruog', 'World'),
    expected=3,
    description='заглавная буква в слове',
    level="full",
)

def task_mp10_crack(cipher, known_word):
    ...
