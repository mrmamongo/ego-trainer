from ego.testing import case

@case(
    args=({'profile': {'name': 'Аня', 'settings': {'theme': 'dark', 'size': None}, 'tags': ['a', 'b']}, 'id': 7}, 'profile.settings.theme'),
    expected='dark',
    description='глубокий путь',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({'profile': {'name': 'Аня', 'settings': {'theme': 'dark', 'size': None}, 'tags': ['a', 'b']}, 'id': 7}, 'id'),
    expected=7,
    description='ключ верхнего уровня',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({'profile': {'name': 'Аня', 'settings': {'theme': 'dark', 'size': None}, 'tags': ['a', 'b']}, 'id': 7}, 'profile.settings.lang', 'ru'),
    expected='ru',
    description='ключа нет: default',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({'profile': {'name': 'Аня', 'settings': {'theme': 'dark', 'size': None}, 'tags': ['a', 'b']}, 'id': 7}, 'profile.settings.size', 'x'),
    expected=None,
    description='значение None найдено, default не нужен',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@case(
    args=({'profile': {'name': 'Аня', 'settings': {'theme': 'dark', 'size': None}, 'tags': ['a', 'b']}, 'id': 7}, 'id.value', '?'),
    expected='?',
    description='дальше идти некуда: число',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({'profile': {'name': 'Аня', 'settings': {'theme': 'dark', 'size': None}, 'tags': ['a', 'b']}, 'id': 7}, 'profile.name.first', '?'),
    expected='?',
    description='дальше идти некуда: строка',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@case(
    args=({'profile': {'name': 'Аня', 'settings': {'theme': 'dark', 'size': None}, 'tags': ['a', 'b']}, 'id': 7}, 'profile.tags.a', '?'),
    expected='?',
    description='дальше идти некуда: список',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@case(
    args=({}, 'a', 5),
    expected=5,
    description='пустой словарь',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({'profile': {'name': 'Аня', 'settings': {'theme': 'dark', 'size': None}, 'tags': ['a', 'b']}, 'id': 7}, 'nothing.at.all'),
    expected=None,
    description='default не передан',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@case(
    args=({'profile': {'name': 'Аня', 'settings': {'theme': 'dark', 'size': None}, 'tags': ['a', 'b']}, 'id': 7}, 'profile.tags'),
    expected=['a', 'b'],
    description='значение может быть списком',
    level="full",
    check_inputs_unchanged=True,
)

def task_rv10_get_path(data, path, default=None):
    ...
