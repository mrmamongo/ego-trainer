from ego.testing import case

@case(
    args=([10, 50, 120, 80],),
    expected=[80, 1],
    description='одно значение вне границ',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([30, 60],),
    expected=[60, 0],
    description='все значения подходят',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[0, 0],
    description='значений нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([-1, 100],),
    expected=[100, 1],
    description='отрицательное и ровно сто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([101],),
    expected=[0, 1],
    description='единственное значение отклонено',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([0, 0],),
    expected=[0, 0],
    description='ноль допустим',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([40, 150, 160, 70],),
    expected=[70, 2],
    description='две ошибки подряд, последнее значение остаётся',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr08_apply(steps):
    ...
