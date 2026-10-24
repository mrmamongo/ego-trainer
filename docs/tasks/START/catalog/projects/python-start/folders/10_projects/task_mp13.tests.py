from ego.testing import case

@case(
    args=('Abcdefg1',),
    expected='надёжный',
    description='нет проблем',
    level="smoke",
)

@case(
    args=('abcdefgh',),
    expected='средний',
    description='две проблемы',
    level="smoke",
)

@case(
    args=('abc',),
    expected='слабый',
    description='три проблемы',
    level="smoke",
)

@case(
    args=('',),
    expected='слабый',
    description='пустой пароль',
    level="full",
)

@case(
    args=('abcdefgh1',),
    expected='средний',
    description='одна проблема',
    level="full",
)

@case(
    args=('12345678',),
    expected='средний',
    description='только цифры',
    level="full",
)

@case(
    args=('ABC',),
    expected='слабый',
    description='заглавные и коротко',
    level="full",
)

@case(
    args=('Xy7Xy7Xy7',),
    expected='надёжный',
    description='длинный и разнообразный',
    level="full",
)

@case(
    args=('ab',),
    expected='слабый',
    description='короткий, без цифр и заглавных',
    level="full",
)

def task_mp13_strength(pw):
    ...
