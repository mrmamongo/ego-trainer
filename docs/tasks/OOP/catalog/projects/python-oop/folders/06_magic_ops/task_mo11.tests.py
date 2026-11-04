from ego.testing import case, rules

@rules(
    require_classes=['Money'],
    require_methods={'Money': ['__init__', '__add__', '__sub__', '__mul__']},
)
@case(
    args=(500, 120, 3),
    expected={'sum': 620, 'diff': 380, 'times': 1500, 'a': 500, 'b': 120, 'new_objects': True},
    description='обычный расчёт',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(0, 0, 5),
    expected={'sum': 0, 'diff': 0, 'times': 0, 'a': 0, 'b': 0, 'new_objects': True},
    description='нули',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, 250, 1),
    expected={'sum': 350, 'diff': -150, 'times': 100, 'a': 100, 'b': 250, 'new_objects': True},
    description='разность отрицательная',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(999, 1, 0),
    expected={'sum': 1000, 'diff': 998, 'times': 0, 'a': 999, 'b': 1, 'new_objects': True},
    description='умножить на ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(12345, 55, 10),
    expected={'sum': 12400, 'diff': 12290, 'times': 123450, 'a': 12345, 'b': 55, 'new_objects': True},
    description='крупные суммы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(7, 7, 2),
    expected={'sum': 14, 'diff': 0, 'times': 14, 'a': 7, 'b': 7, 'new_objects': True},
    description='равные суммы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo11_calc(a, b, k):
    ...
