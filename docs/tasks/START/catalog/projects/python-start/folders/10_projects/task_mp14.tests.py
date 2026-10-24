from ego.testing import case

@case(
    args=('Abcdefg1!',),
    expected=[],
    description='всё хорошо',
    level="smoke",
)

@case(
    args=('Abcdefg1',),
    expected=['no_special'],
    description='нет спецсимвола',
    level="smoke",
)

@case(
    args=('Password',),
    expected=['common', 'no_digit', 'no_special'],
    description='известный пароль в другом регистре',
    level="smoke",
)

@case(
    args=('password',),
    expected=['common', 'no_digit', 'no_upper', 'no_special'],
    description='известный пароль',
    level="full",
)

@case(
    args=('QWERTY',),
    expected=['common', 'short', 'no_digit', 'no_lower', 'no_special'],
    description='известный и короткий',
    level="full",
)

@case(
    args=('',),
    expected=['short', 'no_digit', 'no_upper', 'no_lower', 'no_special'],
    description='пустой пароль',
    level="full",
)

@case(
    args=('Ab1!',),
    expected=['short'],
    description='только короткий',
    level="full",
)

@case(
    args=('abc#',),
    expected=['short', 'no_digit', 'no_upper'],
    description='спецсимвол есть',
    level="full",
)

@case(
    args=('Xk9$mQ2p',),
    expected=[],
    description='хороший пароль',
    level="full",
)

@case(
    args=('123456',),
    expected=['common', 'short', 'no_upper', 'no_lower', 'no_special'],
    description='цифры',
    level="full",
)

@case(
    args=('Abcdefg 1',),
    expected=['no_special'],
    description='пробел не спецсимвол',
    level="full",
)

@case(
    args=('Aa1@bcdef',),
    expected=[],
    description='собака как спецсимвол',
    level="full",
)

def task_mp14_find_problems(pw):
    ...
