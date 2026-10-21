from ego.testing import case


@case(
    args=(1, 2, 1, 2),
    expected=0,
    description='версии равны',
    level="smoke",
)

@case(
    args=(1, 2, 1, 3),
    expected=-1,
    description='решает второй номер: первая старше',
    level="smoke",
)

@case(
    args=(2, 0, 1, 9),
    expected=1,
    description='решает главный номер: первая новее',
    level="smoke",
)

@case(
    args=(1, 5, 2, 0),
    expected=-1,
    description='главный номер меньше, второй — больше',
    level="full",
)

@case(
    args=(3, 1, 3, 0),
    expected=1,
    description='главные равны, второй больше',
    level="full",
)

@case(
    args=(0, 0, 0, 0),
    expected=0,
    description='нулевые версии',
    level="full",
)

@case(
    args=(4, 9, 5, 0),
    expected=-1,
    description='переход на новую главную версию',
    level="full",
)
def task_fn21_compare_versions(major1, minor1, major2, minor2):
    ...
