from ego.testing import case

@case(
    args=('Abcdefg1',),
    expected=[],
    description='всё хорошо',
    level="smoke",
)

@case(
    args=('abc',),
    expected=['short', 'no_digit', 'no_upper'],
    description='три проблемы',
    level="smoke",
)

@case(
    args=('ABCDEFGH1',),
    expected=['no_lower'],
    description='нет строчных',
    level="smoke",
)

@case(
    args=('',),
    expected=['short', 'no_digit', 'no_upper', 'no_lower'],
    description='пустой пароль',
    level="full",
)

@case(
    args=('12345678',),
    expected=['no_upper', 'no_lower'],
    description='только цифры',
    level="full",
)

@case(
    args=('Ab1',),
    expected=['short'],
    description='только короткий',
    level="full",
)

@case(
    args=('abcdefgh1',),
    expected=['no_upper'],
    description='нет заглавных',
    level="full",
)

@case(
    args=('Abcdefgh',),
    expected=['no_digit'],
    description='нет цифры',
    level="full",
)

@case(
    args=('abcdefgh',),
    expected=['no_digit', 'no_upper'],
    description='только строчные',
    level="full",
)

@case(
    args=('Пароль123',),
    expected=[],
    description='русские буквы тоже буквы',
    level="full",
)

def task_mp12_find_problems(pw):
    ...
