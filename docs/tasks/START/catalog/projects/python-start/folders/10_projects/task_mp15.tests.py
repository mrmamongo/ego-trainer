from ego.testing import case

@case(
    args=('Abcdefg1!',),
    expected='Пароль надёжный: всё в порядке.',
    description='всё хорошо',
    level="smoke",
)

@case(
    args=('Abcdefg1',),
    expected='Пароль средний. Что исправить: добавь символ из !@#$%^&*.',
    description='одна проблема',
    level="smoke",
)

@case(
    args=('abcdefgh1!',),
    expected='Пароль средний. Что исправить: добавь заглавную букву.',
    description='нет заглавных',
    level="smoke",
)

@case(
    args=('abc',),
    expected='Пароль слабый. Что исправить: сделай пароль не короче 8 символов, добавь цифру, добавь заглавную букву, добавь символ из !@#$%^&*.',
    description='много проблем',
    level="full",
)

@case(
    args=('password',),
    expected='Пароль слабый. Что исправить: замени слишком известный пароль, добавь цифру, добавь заглавную букву, добавь символ из !@#$%^&*.',
    description='известный пароль',
    level="full",
)

@case(
    args=('',),
    expected='Пароль слабый. Что исправить: сделай пароль не короче 8 символов, добавь цифру, добавь заглавную букву, добавь строчную букву, добавь символ из !@#$%^&*.',
    description='пустой пароль',
    level="full",
)

@case(
    args=('ABCDEFGH1!',),
    expected='Пароль средний. Что исправить: добавь строчную букву.',
    description='нет строчных',
    level="full",
)

@case(
    args=('Abcdefgh!',),
    expected='Пароль средний. Что исправить: добавь цифру.',
    description='нет цифры',
    level="full",
)

@case(
    args=('Xk9$mQ2p',),
    expected='Пароль надёжный: всё в порядке.',
    description='ещё один хороший',
    level="full",
)

def task_mp15_suggest(pw):
    ...
