from ego.testing import case

@case(
    args=(1,),
    expected=3.14,
    description='единичный радиус',
    level="smoke",
)

@case(
    args=(2,),
    expected=12.57,
    description='радиус 2',
    level="smoke",
)

@case(
    args=(10,),
    expected=314.16,
    description='радиус 10',
    level="smoke",
)

@case(
    args=(0,),
    expected=0.0,
    description='нулевой радиус',
    level="full",
)

@case(
    args=(3,),
    expected=28.27,
    description='радиус 3',
    level="full",
)

@case(
    args=(5,),
    expected=78.54,
    description='радиус 5',
    level="full",
)

@case(
    args=(100,),
    expected=31415.93,
    description='большой радиус',
    level="full",
)
def task_n05_circle_area(r):
    ...
