from ego.testing import case, rules

@rules(
    require_classes=['Vector2'],
    require_methods={'Vector2': ['__init__', '__add__']},
)
@case(
    args=([[1, 2], [3, 4], [-1, 0]],),
    expected=[3, 6],
    description='три шага',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[5, 5]],),
    expected=[5, 5],
    description='один шаг',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[0, 0],
    description='пусто',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[1, 1], [-1, -1]],),
    expected=[0, 0],
    description='вернулся в начало',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[0, 10], [0, 10], [0, 10], [0, 10], [0, 10]],),
    expected=[0, 50],
    description='пять одинаковых шагов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo10_path(steps):
    ...
