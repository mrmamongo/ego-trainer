from ego.testing import case, rules

@rules(
    forbid_names=['deepcopy'],
    forbid_imports=['copy'],
    messages={
        'copy': 'Модуль copy использовать нельзя: копируй уровни вручную',
        'deepcopy': 'deepcopy использовать нельзя: копируй уровни вручную',
    },
)
@case(
    args=({'A': {'tags': ['dev'], 'langs': ['ru']}, 'B': {'tags': ['ops', 'qa'], 'langs': []}},),
    expected={'A': {'tags': ['dev'], 'langs': ['ru']}, 'B': {'tags': ['ops', 'qa'], 'langs': []}},
    description='два профиля',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'A': {'tags': [], 'langs': []}},),
    expected={'A': {'tags': [], 'langs': []}},
    description='пустые списки',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({},),
    expected={},
    description='пустой словарь',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'A': {'tags': ['x'], 'langs': ['ru']}, 'B': {'tags': ['x'], 'langs': ['ru']}},),
    expected={'A': {'tags': ['x'], 'langs': ['ru']}, 'B': {'tags': ['x'], 'langs': ['ru']}},
    description='в данных общий список у двух профилей',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, 'B', 'tags'), (0, 'A', 'tags')),),
)
@case(
    args=({'A': {}},),
    expected={'A': {}},
    description='профиль без полей',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'A': {'tags': ['a', 'b', 'c']}},),
    expected={'A': {'tags': ['a', 'b', 'c']}},
    description='длинный список',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_di20_deep_copy_profiles(profiles):
    ...
