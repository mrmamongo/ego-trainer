from ego.testing import case

@case(
    args=([30, 5, 10], 7),
    expected=[23, 0, 3],
    description='три игрока',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 5),
    expected=[],
    description='пустой отряд',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([10], 0),
    expected=[10],
    description='нулевой урон',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([10, 10, 10], 10),
    expected=[0, 0, 0],
    description='ровно в ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([100, 50], 1),
    expected=[99, 49],
    description='по единице урона',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([3, 8, 0], 5),
    expected=[0, 3, 0],
    description='урон больше здоровья у одного',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl19_squad_hp(hps, damage):
    ...
