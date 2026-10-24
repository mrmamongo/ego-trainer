from ego.testing import case

@case(
    args=(123,),
    expected=321,
    description='три цифры',
    level='smoke',
)

@case(
    args=(1230,),
    expected=321,
    description='ноль на конце пропадает',
    level='smoke',
)

@case(
    args=(5,),
    expected=5,
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
    args=(100,),
    expected=1,
    description='два нуля на конце',
    level='full',
)

@case(
    args=(120,),
    expected=21,
    description='один ноль на конце',
    level='full',
)

@case(
    args=(9876,),
    expected=6789,
    description='четыре цифры',
    level='full',
)

@case(
    args=(1001,),
    expected=1001,
    description='палиндром',
    level='full',
)
def task_r15_reverse_number(n):
    ...
