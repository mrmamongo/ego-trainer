from ego.testing import case, rules

@case(
    args=(3,),
    expected=6,
    description='3!',
    level='smoke',
)

@case(
    args=(5,),
    expected=120,
    description='5!',
    level='smoke',
)

@case(
    args=(1,),
    expected=1,
    description='1!',
    level='smoke',
)

@case(
    args=(0,),
    expected=1,
    description='0! равно 1: ответ для пустого набора',
    level='full',
)

@case(
    args=(6,),
    expected=720,
    description='6!',
    level='full',
)

@case(
    args=(10,),
    expected=3628800,
    description='10!',
    level='full',
)

@case(
    args=(2,),
    expected=2,
    description='2!',
    level='full',
)


@rules(
    forbid_names=["factorial"],
    forbid_imports=["math"],
    messages={
        "factorial": "math.factorial использовать нельзя: только цикл for и range",
        "math": "Модуль math использовать нельзя: факториал считай циклом for",
    },
)

def task_r05_factorial(n):
    ...
