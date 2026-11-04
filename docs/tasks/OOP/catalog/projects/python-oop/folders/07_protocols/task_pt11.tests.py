from ego.testing import case, rules

@rules(
    require_classes=['ChatHistory'],
    require_methods={'ChatHistory': ['__init__', '__iter__']},
)
@case(
    args=(['a', 'b', 'c'], 2),
    expected=[[['a', 'b'], ['c']], [['a', 'b'], ['c']]],
    description='три сообщения по две',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'b'], 2),
    expected=[[['a', 'b']], [['a', 'b']]],
    description='ровно одна страница',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'b', 'c'], 0),
    expected=['error', 'размер страницы должен быть больше нуля'],
    description='размер ноль: ошибка',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 3),
    expected=[[], []],
    description='пустая история',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a'], 5),
    expected=[[['a']], [['a']]],
    description='страница больше истории',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'b', 'c', 'd', 'e'], 1),
    expected=[[['a'], ['b'], ['c'], ['d'], ['e']], [['a'], ['b'], ['c'], ['d'], ['e']]],
    description='по одному сообщению',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a'], -1),
    expected=['error', 'размер страницы должен быть больше нуля'],
    description='отрицательный размер: ошибка',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt11_pages(messages, size):
    ...
