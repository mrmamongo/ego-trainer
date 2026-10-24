from ego.testing import case

@case(
    args=(7,),
    expected=True,
    description='простое число',
    level="smoke",
)

@case(
    args=(9,),
    expected=False,
    description='делится на три',
    level="smoke",
)

@case(
    args=(2,),
    expected=True,
    description='двойка',
    level="smoke",
)

@case(
    args=(1,),
    expected=False,
    description='единица не простое',
    level="full",
)

@case(
    args=(0,),
    expected=False,
    description='ноль',
    level="full",
)

@case(
    args=(-7,),
    expected=False,
    description='отрицательное',
    level="full",
)

@case(
    args=(25,),
    expected=False,
    description='квадрат простого',
    level="full",
)

@case(
    args=(91,),
    expected=False,
    description='семь на тринадцать',
    level="full",
)

@case(
    args=(97,),
    expected=True,
    description='большое простое',
    level="full",
)
def task_bk11_is_prime(n):
    ...
