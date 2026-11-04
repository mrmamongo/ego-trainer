from ego.testing import case, rules

@rules(
    require_classes=['Countdown'],
    require_methods={'Countdown': ['__init__', '__iter__', '__next__']},
)
@case(
    args=(3,),
    expected=[[3, 2, 1], [], 3, 2],
    description='от трёх',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(1,),
    expected=[[1], [], 1, 'конец'],
    description='от единицы: второй next даёт «конец»',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(0,),
    expected=[[], [], 'конец', 'конец'],
    description='ноль: отсчёта нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(5,),
    expected=[[5, 4, 3, 2, 1], [], 5, 4],
    description='от пяти',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(-2,),
    expected=[[], [], 'конец', 'конец'],
    description='отрицательное число',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(2,),
    expected=[[2, 1], [], 2, 1],
    description='от двух',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt13_countdown(start):
    ...
