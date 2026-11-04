from ego.testing import case, rules

@rules(
    require_classes=['Money'],
    require_methods={'Money': ['__init__', '__add__']},
)
@case(
    args=([[100, 'money', 50, False]],),
    expected=[[150, False]],
    description='деньги и деньги',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[100, 'number', 5, False]],),
    expected=[['TypeError', True]],
    description='деньги и число',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[100, 'text', 'руб', False]],),
    expected=[['TypeError', True]],
    description='деньги и строка',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[100, 'number', 5, True]],),
    expected=[['TypeError', True]],
    description='число плюс деньги',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[0, 'money', 0, True]],),
    expected=[[0, False]],
    description='ноль плюс ноль',
    level='full',
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
    args=([[1, 'money', 2, False], [3, 'text', 'x', False], [4, 'money', 5, True]],),
    expected=[[3, False], ['TypeError', True], [9, False]],
    description='смесь',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo12_add(rows):
    ...
