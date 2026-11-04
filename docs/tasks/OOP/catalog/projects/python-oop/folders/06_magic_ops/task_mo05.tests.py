from ego.testing import case, rules

@rules(
    require_classes=['Vector2'],
    require_methods={'Vector2': ['__init__', '__add__']},
)
@case(
    args=([1, 2], [3, 4]),
    expected={'result': [4, 6], 'start': [1, 2], 'step': [3, 4], 'same_object': False},
    description='обычный шаг',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([0, 0], [5, -5]),
    expected={'result': [5, -5], 'start': [0, 0], 'step': [5, -5], 'same_object': False},
    description='из начала координат',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([10, 10], [0, 0]),
    expected={'result': [10, 10], 'start': [10, 10], 'step': [0, 0], 'same_object': False},
    description='нулевой шаг',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([-3, 4], [3, -4]),
    expected={'result': [0, 0], 'start': [-3, 4], 'step': [3, -4], 'same_object': False},
    description='шаг в ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([100, 200], [1, 1]),
    expected={'result': [101, 201], 'start': [100, 200], 'step': [1, 1], 'same_object': False},
    description='большие числа',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo05_move(start, step):
    ...
