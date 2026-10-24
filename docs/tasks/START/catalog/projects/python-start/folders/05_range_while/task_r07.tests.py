from ego.testing import case, rules

@case(
    args=(7,),
    expected=True,
    description='простое',
    level='smoke',
)

@case(
    args=(9,),
    expected=False,
    description='составное: 3 * 3',
    level='smoke',
)

@case(
    args=(2,),
    expected=True,
    description='самое маленькое простое',
    level='smoke',
)

@case(
    args=(1,),
    expected=False,
    description='единица не простая',
    level='full',
)

@case(
    args=(0,),
    expected=False,
    description='ноль',
    level='full',
)

@case(
    args=(-5,),
    expected=False,
    description='отрицательное',
    level='full',
)

@case(
    args=(4,),
    expected=False,
    description='чётное',
    level='full',
)

@case(
    args=(29,),
    expected=True,
    description='простое побольше',
    level='full',
)

@case(
    args=(49,),
    expected=False,
    description='квадрат простого',
    level='full',
)

@case(
    args=(97,),
    expected=True,
    description='ещё одно простое',
    level='full',
)


@rules(
    forbid_imports=["itertools", "math"],
    messages={
        "itertools": "Готовые проверки простоты (itertools.isqrt) использовать нельзя: цикл",
        "math": "Модуль math использовать нельзя: ищи делитель циклом",
    },
)

def task_r07_is_prime(n):
    ...
