from ego.testing import case

@case(
    args=({'A': {'name': 'Аня', 'prefs': {'language': 'ru', 'theme': 'dark'}}, 'B': {'name': 'Боря', 'prefs': {'language': 'ru', 'theme': 'dark'}}}, 'A', 'en'),
    expected={'A': {'name': 'Аня', 'prefs': {'language': 'en', 'theme': 'dark'}}, 'B': {'name': 'Боря', 'prefs': {'language': 'ru', 'theme': 'dark'}}},
    description='у A и B общий prefs: меняется только A',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, 'B', 'prefs'), (0, 'A', 'prefs')),),
)
@case(
    args=({'A': {'name': 'Аня', 'prefs': {'language': 'ru', 'theme': 'dark'}}, 'B': {'name': 'Боря', 'prefs': {'language': 'de', 'theme': 'light'}}}, 'B', 'fr'),
    expected={'A': {'name': 'Аня', 'prefs': {'language': 'ru', 'theme': 'dark'}}, 'B': {'name': 'Боря', 'prefs': {'language': 'fr', 'theme': 'light'}}},
    description='раздельные prefs: входные данные остаются прежними',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'A': {'name': 'Аня', 'prefs': {'language': 'ru', 'theme': 'dark'}}}, 'Z', 'en'),
    expected={'A': {'name': 'Аня', 'prefs': {'language': 'ru', 'theme': 'dark'}}},
    description='неизвестный пользователь: копия без изменений',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, 'A', 'en'),
    expected={},
    description='пустые профили',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'A': {'name': 'Аня', 'prefs': {'language': 'ru', 'theme': 'dark'}}, 'B': {'name': 'Боря', 'prefs': {'language': 'ru', 'theme': 'dark'}}, 'C': {'name': 'Ева', 'prefs': {'language': 'ru', 'theme': 'dark'}}}, 'B', 'es'),
    expected={'A': {'name': 'Аня', 'prefs': {'language': 'ru', 'theme': 'dark'}}, 'B': {'name': 'Боря', 'prefs': {'language': 'es', 'theme': 'dark'}}, 'C': {'name': 'Ева', 'prefs': {'language': 'ru', 'theme': 'dark'}}},
    description='общий prefs у A и C: меняется только B',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, 'C', 'prefs'), (0, 'A', 'prefs')),),
)
@case(
    args=({'A': {'name': 'Аня', 'prefs': {'language': 'ru', 'theme': 'dark'}}, 'B': {'name': 'Боря', 'prefs': {'language': 'ru', 'theme': 'dark'}}}, 'B', 'ru'),
    expected={'A': {'name': 'Аня', 'prefs': {'language': 'ru', 'theme': 'dark'}}, 'B': {'name': 'Боря', 'prefs': {'language': 'ru', 'theme': 'dark'}}},
    description='тот же язык: ничего не меняется, но результат независим',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, 'B', 'prefs'), (0, 'A', 'prefs')),),
)
def task_di19_set_language(profiles, user, lang):
    ...
