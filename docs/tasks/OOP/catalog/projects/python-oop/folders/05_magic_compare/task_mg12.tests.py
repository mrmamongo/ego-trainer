from ego.testing import case, rules

@rules(
    require_classes=['Money'],
    require_methods={'Money': ['__init__', '__eq__']},
)
@case(
    args=([[500, 500]],),
    expected=[[True, False, False, True]],
    description='равные суммы',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[500, 700]],),
    expected=[[False, True, False, True]],
    description='разные суммы',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[0, 0], [1, 0]],),
    expected=[[True, False, False, True], [False, True, False, True]],
    description='нули и единица',
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
    args=([[100, 100], [100, 101], [250, 250]],),
    expected=[[True, False, False, True], [False, True, False, True], [True, False, False, True]],
    description='несколько пар',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[12345, 12345]],),
    expected=[[True, False, False, True]],
    description='большая сумма',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg12_compare(pairs):
    ...
