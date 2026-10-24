from ego.testing import case

@case(
    args=(3,),
    expected=[3, 2, 1],
    description='от трёх',
    level='smoke',
)

@case(
    args=(1,),
    expected=[1],
    description='только единица',
    level='smoke',
)

@case(
    args=(5,),
    expected=[5, 4, 3, 2, 1],
    description='от пяти',
    level='smoke',
)

@case(
    args=(0,),
    expected=[],
    description='ноль: считать нечего',
    level='full',
)

@case(
    args=(10,),
    expected=[10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
    description='от десяти',
    level='full',
)

@case(
    args=(2,),
    expected=[2, 1],
    description='два числа',
    level='full',
)
def task_r09_countdown(n):
    ...
