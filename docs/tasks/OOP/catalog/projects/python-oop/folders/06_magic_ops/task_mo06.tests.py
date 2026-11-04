from ego.testing import case, rules

@rules(
    require_classes=['Money'],
    require_methods={'Money': ['__init__', '__add__']},
)
@case(
    args=([[100, 'money', 50], [100, 'number', 5]],),
    expected=[150, 'TypeError'],
    description='деньги и число',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[0, 'money', 0]],),
    expected=[0],
    description='ноль плюс ноль',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[250, 'text', 'руб']],),
    expected=['TypeError'],
    description='деньги и строка',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[],
    description='пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[1, 'money', 2], [3, 'money', 4], [5, 'number', 6], [7, 'text', 'x']],),
    expected=[3, 7, 'TypeError', 'TypeError'],
    description='смесь',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo06_add(rows):
    ...
