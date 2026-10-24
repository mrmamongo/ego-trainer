from ego.testing import case

@case(
    args=(1000, 10, 1100),
    expected=1,
    description='ровно цель за год',
    level='smoke',
)

@case(
    args=(1000, 10, 1500),
    expected=5,
    description='несколько лет',
    level='smoke',
)

@case(
    args=(1000, 10, 1000),
    expected=0,
    description='цель уже достигнута',
    level='smoke',
)

@case(
    args=(200, 5, 150),
    expected=0,
    description='цель ниже баланса',
    level='full',
)

@case(
    args=(100, 100, 1000),
    expected=4,
    description='удвоение каждый год',
    level='full',
)

@case(
    args=(100, 1, 102),
    expected=2,
    description='маленький процент: прирост по 1',
    level='full',
)

@case(
    args=(1000, 50, 10000),
    expected=6,
    description='полтора раза в год',
    level='full',
)

@case(
    args=(500, 20, 501),
    expected=1,
    description='достаточно одного года',
    level='full',
)
def task_r17_years_to_target(balance, percent, target):
    ...
