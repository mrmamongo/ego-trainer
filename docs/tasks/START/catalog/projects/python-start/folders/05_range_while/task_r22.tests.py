from ego.testing import case

@case(
    args=(12, 18),
    expected=6,
    description='НОД двух составных',
    level='smoke',
)

@case(
    args=(7, 13),
    expected=1,
    description='взаимно простые',
    level='smoke',
)

@case(
    args=(100, 75),
    expected=25,
    description='первое больше',
    level='smoke',
)

@case(
    args=(0, 5),
    expected=5,
    description='первое равно нулю',
    level='full',
)

@case(
    args=(5, 0),
    expected=5,
    description='второе равно нулю',
    level='full',
)

@case(
    args=(10, 10),
    expected=10,
    description='числа равны',
    level='full',
)

@case(
    args=(48, 18),
    expected=6,
    description='пример из карточки',
    level='full',
)

@case(
    args=(17, 0),
    expected=17,
    description='простое и ноль',
    level='full',
)

@case(
    args=(1071, 462),
    expected=21,
    description='классический пример',
    level='full',
)

@case(
    args=(270, 192),
    expected=6,
    description='большие числа',
    level='full',
)
def task_r22_gcd(a, b):
    ...
