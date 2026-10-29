from ego.testing import case

@case(
    args=({'name': 'Аня', 'level': 1, 'tags': ['new']}, [('set', 'level', 2), ('add_tag', 'dev'), ('remove_tag', 'new')]),
    expected={'name': 'Аня', 'level': 2, 'tags': ['dev']},
    description='все три вида правок',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({'name': 'Боря', 'level': 3, 'tags': []}, [('set', 'name', 'Борис')]),
    expected={'name': 'Борис', 'level': 3, 'tags': []},
    description='только поле',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({'name': 'Вика', 'level': 1, 'tags': ['a']}, [('add_tag', 'b'), ('add_tag', 'a')]),
    expected={'name': 'Вика', 'level': 1, 'tags': ['a', 'b']},
    description='повторный тег не добавляется',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({'name': 'Яна', 'level': 5, 'tags': ['x', 'y']}, []),
    expected={'name': 'Яна', 'level': 5, 'tags': ['x', 'y']},
    description='нет правок: копия, не тот же объект',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({'name': 'Олег', 'level': 2, 'tags': ['x']}, [('remove_tag', 'zzz')]),
    expected={'name': 'Олег', 'level': 2, 'tags': ['x']},
    description='убрать несуществующий тег',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({'name': 'Ира', 'level': 1, 'tags': ['a', 'b', 'c']}, [('remove_tag', 'b'), ('add_tag', 'b'), ('set', 'level', 9)]),
    expected={'name': 'Ира', 'level': 9, 'tags': ['a', 'c', 'b']},
    description='убрали и вернули в конец',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({'name': 'Лена', 'level': 4, 'tags': ['t']}, [('set', 'name', 'А'), ('set', 'name', 'Б')]),
    expected={'name': 'Б', 'level': 4, 'tags': ['t']},
    description='последняя правка выигрывает',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_rv11_apply_changes(profile, changes):
    ...
