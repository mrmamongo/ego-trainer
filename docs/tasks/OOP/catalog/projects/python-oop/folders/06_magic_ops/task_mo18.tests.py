from ego.testing import case, rules

@rules(
    require_classes=['Vector2'],
    require_methods={'Vector2': ['__init__', '__mul__', '__rmul__']},
)
@case(
    args=(1, 2, 3),
    expected=[[3, 6], [3, 6]],
    description='число справа и слева',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(1, 2, 'a'),
    expected=['TypeError', 'TypeError'],
    description='строка вместо числа',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(0, 0, 5),
    expected=[[0, 0], [0, 0]],
    description='нулевой вектор',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(-1, 4, -2),
    expected=[[2, -8], [2, -8]],
    description='отрицательный множитель',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(2, 3, 0),
    expected=[[0, 0], [0, 0]],
    description='ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(2, 3, 0.5),
    expected=[[1.0, 1.5], [1.0, 1.5]],
    description='дробь',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo18_scale(x, y, k):
    ...
