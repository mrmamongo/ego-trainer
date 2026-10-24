from ego.testing import case

@case(
    args=(13, 4),
    expected=4,
    description='остаток — нужна ещё коробка',
    level="smoke",
)

@case(
    args=(12, 4),
    expected=3,
    description='делится ровно',
    level="smoke",
)

@case(
    args=(0, 4),
    expected=0,
    description='предметов нет',
    level="smoke",
)

@case(
    args=(1, 10),
    expected=1,
    description='один предмет',
    level="full",
)

@case(
    args=(100, 7),
    expected=15,
    description='14 полных и остаток 2',
    level="full",
)

@case(
    args=(7, 1),
    expected=7,
    description='по одному в коробке',
    level="full",
)
def task_n06_boxes(items, per_box):
    ...
