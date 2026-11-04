from ego.testing import case, rules

@rules(
    require_classes=['Vector2'],
    require_methods={'Vector2': ['__init__', '__add__', '__mul__']},
)
@case(
    args=(2, 3, 4),
    expected={'scaled': [8, 12], 'original': [2, 3]},
    description='обычное умножение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(1, 1, 0),
    expected={'scaled': [0, 0], 'original': [1, 1]},
    description='на ноль',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(-2, 5, 3),
    expected={'scaled': [-6, 15], 'original': [-2, 5]},
    description='отрицательная координата',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(0, 0, 10),
    expected={'scaled': [0, 0], 'original': [0, 0]},
    description='нулевой вектор',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(3, -4, -1),
    expected={'scaled': [-3, 4], 'original': [3, -4]},
    description='на минус один',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(1, 2, 1.5),
    expected={'scaled': [1.5, 3.0], 'original': [1, 2]},
    description='дробный множитель',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo08_scale(x, y, k):
    ...
