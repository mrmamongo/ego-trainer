from ego.testing import case

@case(
    args=(507,),
    expected=12,
    description='5 + 0 + 7',
    level='smoke',
)

@case(
    args=(123,),
    expected=6,
    description='1 + 2 + 3',
    level='smoke',
)

@case(
    args=(9,),
    expected=9,
    description='одна цифра',
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
    args=(999,),
    expected=27,
    description='три девятки',
    level='full',
)

@case(
    args=(123456,),
    expected=21,
    description='шесть цифр',
    level='full',
)

@case(
    args=(1000,),
    expected=1,
    description='единица и нули',
    level='full',
)
def task_r14_digit_sum(n):
    ...
