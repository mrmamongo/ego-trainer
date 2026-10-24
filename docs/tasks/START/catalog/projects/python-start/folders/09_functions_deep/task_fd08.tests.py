from ego.testing import case

@case(
    args=(100,),
    expected=6,
    description='сто баллов дают шесть',
    level="smoke",
)

@case(
    args=(90,),
    expected=5,
    description='старая пятёрка',
    level="smoke",
)

@case(
    args=(60,),
    expected=3,
    description='старая тройка',
    level="smoke",
)

@case(
    args=(99,),
    expected=5,
    description='99 всё ещё пятёрка',
    level="full",
)

@case(
    args=(85,),
    expected=5,
    description='граница пятёрки',
    level="full",
)

@case(
    args=(84,),
    expected=4,
    description='чуть ниже границы пятёрки',
    level="full",
)

@case(
    args=(70,),
    expected=4,
    description='граница четвёрки',
    level="full",
)

@case(
    args=(50,),
    expected=3,
    description='граница тройки',
    level="full",
)

@case(
    args=(49,),
    expected=2,
    description='двойка у границы',
    level="full",
)

@case(
    args=(0,),
    expected=2,
    description='ноль баллов',
    level="full",
)

def task_fd08_grade(score):
    ...
