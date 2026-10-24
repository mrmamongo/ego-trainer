from ego.testing import case

@case(
    args=({'name': 'Аня', 'tags': ['dev']}, 'admin'),
    expected={'name': 'Аня', 'tags': ['dev', 'admin']},
    description='новый тег добавлен в конец',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'name': 'Боря', 'tags': ['dev']}, 'dev'),
    expected={'name': 'Боря', 'tags': ['dev']},
    description='такой тег уже есть: не дублируется',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'name': 'Вика', 'tags': []}, 'new'),
    expected={'name': 'Вика', 'tags': ['new']},
    description='у профиля не было тегов',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'name': 'Гена', 'tags': ['a', 'b'], 'level': 3}, 'c'),
    expected={'name': 'Гена', 'tags': ['a', 'b', 'c'], 'level': 3},
    description='другие поля сохраняются',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'name': 'Даша', 'tags': ['x']}, 'y'),
    expected={'name': 'Даша', 'tags': ['x', 'y']},
    description='вход и результат независимы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_di21_add_tag(profile, tag):
    ...
