from ego.testing import case, rules

@rules(
    require_classes=['Countdown'],
    require_methods={'Countdown': ['__init__', '__iter__']},
)
@case(
    args=(3,),
    expected=[['3 сек', '2 сек', '1 сек'], ['3 сек', '2 сек', '1 сек']],
    description='три секунды',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(1,),
    expected=[['1 сек'], ['1 сек']],
    description='одна секунда',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(2,),
    expected=[['2 сек', '1 сек'], ['2 сек', '1 сек']],
    description='две секунды',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(0,),
    expected=[[], []],
    description='ноль: отсчёта нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(5,),
    expected=[['5 сек', '4 сек', '3 сек', '2 сек', '1 сек'], ['5 сек', '4 сек', '3 сек', '2 сек', '1 сек']],
    description='пять секунд',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(-2,),
    expected=[[], []],
    description='отрицательное число: отсчёта нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt08_timer(start):
    ...
