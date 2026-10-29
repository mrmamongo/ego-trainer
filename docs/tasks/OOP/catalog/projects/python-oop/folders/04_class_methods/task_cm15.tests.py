from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_methods={'Player': ['__init__', 'from_dict']},
    require_decorators={'Player.from_dict': ['classmethod']},
    forbid_names=['Player'],
    allow_in=['task_cm15_load'],
    messages={
        'Player': 'Внутри класса создавай объект через cls(...), а не по имени Player',
    },
)
@case(
    args=({'name': 'Аня', 'hp': 30, 'level': 3},),
    expected=['Аня', 30, 3],
    description='все поля в сохранении',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'name': 'Боря'},),
    expected=['Боря', 100, 1],
    description='hp и level по умолчанию',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'name': 'Вика', 'hp': 0},),
    expected=['Вика', 0, 1],
    description='hp равно нулю — это не «нет значения»',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'name': 'Юра', 'level': 5, 'gold': 99},),
    expected=['Юра', 100, 5],
    description='лишний ключ игнорируется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'hp': 10, 'name': 'Ира', 'tags': []},),
    expected=['Ира', 10, 1],
    description='порядок ключей не важен',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'name': 'Лев', 'level': 0},),
    expected=['Лев', 100, 0],
    description='уровень ноль сохраняется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm15_load(save):
    ...
