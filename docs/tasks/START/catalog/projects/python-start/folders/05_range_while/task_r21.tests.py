from ego.testing import case

@case(
    args=(38,),
    expected=2,
    description='38 -> 11 -> 2',
    level='smoke',
)

@case(
    args=(507,),
    expected=3,
    description='507 -> 12 -> 3',
    level='smoke',
)

@case(
    args=(7,),
    expected=7,
    description='уже однозначное',
    level='smoke',
)

@case(
    args=(0,),
    expected=0,
    description='ноль',
    level='full',
)

@case(
    args=(10,),
    expected=1,
    description='десять',
    level='full',
)

@case(
    args=(99,),
    expected=9,
    description='99 -> 18 -> 9',
    level='full',
)

@case(
    args=(9875,),
    expected=2,
    description='9875 -> 29 -> 11 -> 2',
    level='full',
)

@case(
    args=(12345,),
    expected=6,
    description='12345 -> 15 -> 6',
    level='full',
)

@case(
    args=(999999,),
    expected=9,
    description='шесть девяток',
    level='full',
)

@case(
    args=(493193,),
    expected=2,
    description='493193 -> 29 -> 11 -> 2',
    level='full',
)
def task_r21_digital_root(n):
    ...
