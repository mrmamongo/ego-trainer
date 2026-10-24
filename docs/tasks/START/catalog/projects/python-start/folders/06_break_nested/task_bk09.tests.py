from ego.testing import case, rules

@case(
    args=(['go', 'go', 'stop', 'go'],),
    expected=2,
    description='стоп посередине',
    level="smoke",
)

@case(
    args=(['go', 'turn'],),
    expected=2,
    description='стопа нет',
    level="smoke",
)

@case(
    args=(['stop', 'go'],),
    expected=0,
    description='стоп первым',
    level="smoke",
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=(['go', 'stop', 'stop'],),
    expected=1,
    description='два стопа подряд',
    level="full",
)

@case(
    args=(['Stop', 'go'],),
    expected=2,
    description='регистр важен',
    level="full",
)

@case(
    args=(['a', 'b', 'c', 'd', 'stop'],),
    expected=4,
    description='стоп в конце',
    level="full",
)


@rules(forbid_names=["len"])

def task_bk09_count_commands(commands):
    ...
