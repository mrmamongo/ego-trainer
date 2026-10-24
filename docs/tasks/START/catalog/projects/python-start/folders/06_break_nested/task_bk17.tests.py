from ego.testing import case

@case(
    args=(3,),
    expected=['*', '**', '***'],
    description='три ряда',
    level="smoke",
)

@case(
    args=(1,),
    expected=['*'],
    description='один ряд',
    level="smoke",
)

@case(
    args=(2,),
    expected=['*', '**'],
    description='два ряда',
    level="smoke",
)

@case(
    args=(0,),
    expected=[],
    description='нет рядов',
    level="full",
)

@case(
    args=(5,),
    expected=['*', '**', '***', '****', '*****'],
    description='пять рядов',
    level="full",
)

@case(
    args=(4,),
    expected=['*', '**', '***', '****'],
    description='четыре ряда',
    level="full",
)
def task_bk17_staircase(n):
    ...
