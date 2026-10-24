from ego.testing import case

@case(
    args=(1,),
    expected=1,
    description='одна пара',
    level="smoke",
)

@case(
    args=(2,),
    expected=9,
    description='две строки',
    level="smoke",
)

@case(
    args=(3,),
    expected=36,
    description='три на три',
    level="smoke",
)

@case(
    args=(0,),
    expected=0,
    description='нет пар',
    level="full",
)

@case(
    args=(4,),
    expected=100,
    description='четыре на четыре',
    level="full",
)

@case(
    args=(5,),
    expected=225,
    description='пять на пять',
    level="full",
)

@case(
    args=(10,),
    expected=3025,
    description='десять на десять',
    level="full",
)
def task_bk14_table_sum(n):
    ...
