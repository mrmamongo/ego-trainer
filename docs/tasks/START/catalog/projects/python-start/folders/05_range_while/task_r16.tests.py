from ego.testing import case, rules

@case(
    args=(507,),
    expected=12,
    description='теряется старшая цифра 5',
    level='smoke',
)

@case(
    args=(5,),
    expected=5,
    description='однозначное число',
    level='smoke',
)

@case(
    args=(123,),
    expected=6,
    description='три цифры',
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
    description='ноль в конце',
    level='full',
)

@case(
    args=(99,),
    expected=18,
    description='две девятки',
    level='full',
)

@case(
    args=(4096,),
    expected=19,
    description='четыре цифры',
    level='full',
)


@rules(forbid_names=["str", "sum"])

def task_r16_digit_sum(n):
    ...
