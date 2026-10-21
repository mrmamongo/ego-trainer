from ego.testing import case


@case(
    args=(100,),
    expected=5,
    description='максимум — пятёрка',
    level="smoke",
)

@case(
    args=(75,),
    expected=4,
    description='75 — нижняя граница четвёрки',
    level="smoke",
)

@case(
    args=(60,),
    expected=3,
    description='60 — нижняя граница тройки',
    level="smoke",
)

@case(
    args=(59,),
    expected=2,
    description='59 — двойка',
    level="smoke",
)

@case(
    args=(90,),
    expected=5,
    description='90 — нижняя граница пятёрки',
    level="full",
)

@case(
    args=(89,),
    expected=4,
    description='89 — верхняя граница четвёрки',
    level="full",
)

@case(
    args=(74,),
    expected=3,
    description='74 — верхняя граница тройки',
    level="full",
)

@case(
    args=(0,),
    expected=2,
    description='ноль баллов',
    level="full",
)
def task_fn11_mark(score):
    ...
