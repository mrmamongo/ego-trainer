from ego.testing import case

@case(
    args=(6,),
    expected=8,
    description='пример из карточки',
    level='smoke',
)

@case(
    args=(2,),
    expected=1,
    description='один шаг',
    level='smoke',
)

@case(
    args=(3,),
    expected=7,
    description='3, 10, 5, 16, 8, 4, 2, 1',
    level='smoke',
)

@case(
    args=(1,),
    expected=0,
    description='уже единица',
    level='full',
)

@case(
    args=(4,),
    expected=2,
    description='4, 2, 1',
    level='full',
)

@case(
    args=(16,),
    expected=4,
    description='степень двойки',
    level='full',
)

@case(
    args=(7,),
    expected=16,
    description='длинная цепочка',
    level='full',
)

@case(
    args=(27,),
    expected=111,
    description='знаменитое число 27',
    level='full',
)
def task_r18_collatz_steps(n):
    ...
