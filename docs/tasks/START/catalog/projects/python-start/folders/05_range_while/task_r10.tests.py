from ego.testing import case

@case(
    args=(3,),
    expected=14,
    description='1 + 4 + 9',
    level='smoke',
)

@case(
    args=(1,),
    expected=1,
    description='только единица',
    level='smoke',
)

@case(
    args=(4,),
    expected=30,
    description='1 + 4 + 9 + 16',
    level='smoke',
)

@case(
    args=(0,),
    expected=0,
    description='n равно нулю',
    level='full',
)

@case(
    args=(2,),
    expected=5,
    description='1 + 4',
    level='full',
)

@case(
    args=(10,),
    expected=385,
    description='до десяти',
    level='full',
)
def task_r10_sum_squares(n):
    ...
