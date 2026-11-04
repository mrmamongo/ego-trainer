from ego.testing import case, rules

@rules(
    require_classes=['Score'],
    require_methods={'Score': ['__init__', '__add__', '__radd__']},
)
@case(
    args=([5, 7, 3],),
    expected=15,
    description='три раунда',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([10],),
    expected=10,
    description='один раунд',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([0, 0],),
    expected=0,
    description='нули',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=0,
    description='пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([-5, 5, 100],),
    expected=100,
    description='отрицательные очки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo09_total(points):
    ...
