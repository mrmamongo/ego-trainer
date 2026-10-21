from ego.testing import case


@case(
    args=(2024,),
    expected=True,
    description='делится на 4',
    level="smoke",
)

@case(
    args=(2023,),
    expected=False,
    description='не делится на 4',
    level="smoke",
)

@case(
    args=(1900,),
    expected=False,
    description='делится на 100, но не на 400',
    level="smoke",
)

@case(
    args=(2000,),
    expected=True,
    description='делится на 400',
    level="full",
)

@case(
    args=(2100,),
    expected=False,
    description='век, не делящийся на 400',
    level="full",
)

@case(
    args=(2400,),
    expected=True,
    description='делится на 400',
    level="full",
)

@case(
    args=(4,),
    expected=True,
    description='самый ранний високосный',
    level="full",
)
def task_fn13_is_leap(year):
    ...
