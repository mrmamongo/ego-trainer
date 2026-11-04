from ego.testing import case, rules

@rules(
    require_classes=['Score'],
    require_methods={'Score': ['__init__', '__add__', '__radd__']},
)
@case(
    args=([3, 4, 5], 0),
    expected=12,
    description='три раунда',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([7], 0),
    expected=7,
    description='один раунд',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 0),
    expected=0,
    description='пусто',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([3, 4], 5),
    expected='TypeError',
    description='чужое начало даёт ошибку',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 5),
    expected=5,
    description='пусто с началом пять',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([-2, 2], 0),
    expected=0,
    description='минус и плюс',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo13_total(points, start):
    ...
