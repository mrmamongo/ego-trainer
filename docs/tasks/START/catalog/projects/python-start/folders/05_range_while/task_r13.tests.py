from ego.testing import case

@case(
    args=(507,),
    expected=3,
    description='три цифры',
    level='smoke',
)

@case(
    args=(7,),
    expected=1,
    description='одна цифра',
    level='smoke',
)

@case(
    args=(12345,),
    expected=5,
    description='пять цифр',
    level='smoke',
)

@case(
    args=(0,),
    expected=1,
    description='у нуля одна цифра',
    level='full',
)

@case(
    args=(10,),
    expected=2,
    description='ноль в конце',
    level='full',
)

@case(
    args=(100,),
    expected=3,
    description='два нуля в конце',
    level='full',
)

@case(
    args=(99999999,),
    expected=8,
    description='восемь девяток',
    level='full',
)

@case(
    args=(1000000,),
    expected=7,
    description='миллион',
    level='full',
)
def task_r13_count_digits(n):
    ...
