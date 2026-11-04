from ego.testing import case, rules

@rules(
    require_functions=['save_profile', 'load_profile'],
)
@case(
    args=('Аня', 3, ['меч', 'щит']),
    expected=['{"name": "Аня", "level": 3, "items": ["меч", "щит"]}', 'Аня', 3, ['меч', 'щит']],
    description='профиль с предметами',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('Боря', 1, []),
    expected=['{"name": "Боря", "level": 1, "items": []}', 'Боря', 1, []],
    description='пустой инвентарь',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('Z', 10, ['potion']),
    expected=['{"name": "Z", "level": 10, "items": ["potion"]}', 'Z', 10, ['potion']],
    description='латинское имя',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('Вика', 0, []),
    expected=['{"name": "Вика", "level": 0, "items": []}', 'Вика', 0, []],
    description='нулевой уровень',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('Гена Иванов', 99, ['зелье', 'зелье']),
    expected=['{"name": "Гена Иванов", "level": 99, "items": ["зелье", "зелье"]}', 'Гена Иванов', 99, ['зелье', 'зелье']],
    description='имя с пробелом, повторы предметов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('О"Коннор', 5, ['ключ']),
    expected=['{"name": "О\\"Коннор", "level": 5, "items": ["ключ"]}', 'О"Коннор', 5, ['ключ']],
    description='кавычка в имени',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt16_roundtrip(name, level, items):
    ...
