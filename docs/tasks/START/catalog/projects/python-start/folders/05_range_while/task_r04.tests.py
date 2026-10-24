from ego.testing import case, rules

@case(
    args=(3,),
    expected=6,
    description='от 1 до 3',
    level='smoke',
)

@case(
    args=(5,),
    expected=15,
    description='от 1 до 5',
    level='smoke',
)

@case(
    args=(10,),
    expected=55,
    description='от 1 до 10',
    level='smoke',
)

@case(
    args=(1,),
    expected=1,
    description='одно число',
    level='full',
)

@case(
    args=(0,),
    expected=0,
    description='n равно нулю: слагаемых нет',
    level='full',
)

@case(
    args=(100,),
    expected=5050,
    description='сто чисел',
    level='full',
)

@case(
    args=(2,),
    expected=3,
    description='два числа',
    level='full',
)


@rules(forbid_names=["sum"])

def task_r04_sum_to(n):
    ...
