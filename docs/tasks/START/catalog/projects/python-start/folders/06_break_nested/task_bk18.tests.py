from ego.testing import case

@case(
    args=(7,),
    expected=6,
    description='самая частая сумма',
    level="smoke",
)

@case(
    args=(2,),
    expected=1,
    description='минимум',
    level="smoke",
)

@case(
    args=(3,),
    expected=2,
    description='порядок важен',
    level="smoke",
)

@case(
    args=(12,),
    expected=1,
    description='максимум',
    level="full",
)

@case(
    args=(1,),
    expected=0,
    description='слишком мало',
    level="full",
)

@case(
    args=(13,),
    expected=0,
    description='слишком много',
    level="full",
)

@case(
    args=(0,),
    expected=0,
    description='ноль',
    level="full",
)

@case(
    args=(8,),
    expected=5,
    description='после семи',
    level="full",
)

@case(
    args=(6,),
    expected=5,
    description='перед семью',
    level="full",
)
def task_bk18_dice_ways(total):
    ...
