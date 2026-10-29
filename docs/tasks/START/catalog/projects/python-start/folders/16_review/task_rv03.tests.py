from ego.testing import case

@case(
    args=('  Anna_7 ',),
    expected='ok',
    description='пробелы и заглавная буква',
    level="smoke",
)

@case(
    args=(' ab ',),
    expected='too_short',
    description='пробелы не считаются в длину',
    level="smoke",
)

@case(
    args=('an na',),
    expected='bad_char',
    description='пробел внутри',
    level="smoke",
)

@case(
    args=('',),
    expected='too_short',
    description='пустая строка',
    level="full",
)

@case(
    args=('ab!',),
    expected='bad_char',
    description='длина 3, но есть запрещённый символ',
    level="full",
    hide_expected=True,
)

@case(
    args=('a-b',),
    expected='bad_char',
    description='дефис не разрешён',
    level="full",
)

@case(
    args=('BOB',),
    expected='ok',
    description='заглавные буквы допустимы после lower',
    level="full",
    hide_expected=True,
)

@case(
    args=('   ',),
    expected='too_short',
    description='только пробелы',
    level="full",
)

@case(
    args=('___',),
    expected='ok',
    description='подчёркивания допустимы',
    level="full",
    hide_expected=True,
)

@case(
    args=('анна',),
    expected='bad_char',
    description='кириллица не разрешена',
    level="full",
    hide_expected=True,
)

@case(
    args=('!!',),
    expected='too_short',
    description='сначала проверяется длина',
    level="full",
)

def task_rv03_check_username(raw):
    ...
