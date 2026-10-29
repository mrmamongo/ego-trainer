from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_methods={'Player': ['__init__', '__repr__', '__str__']},
)
@case(
    args=([['Аня', 120]],),
    expected=[['Аня: 120', "Player('Аня', 120)", 'Аня: 120']],
    description='один игрок',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Боря', 0]],),
    expected=[['Боря: 0', "Player('Боря', 0)", 'Боря: 0']],
    description='ноль очков',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Вика', 95], ['Гена', 100]],),
    expected=[['Вика: 95', "Player('Вика', 95)", 'Вика: 95'], ['Гена: 100', "Player('Гена', 100)", 'Гена: 100']],
    description='два игрока',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[],
    description='пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Мария Ивановна', 7]],),
    expected=[['Мария Ивановна: 7', "Player('Мария Ивановна', 7)", 'Мария Ивановна: 7']],
    description='имя с пробелом',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Ира', -5]],),
    expected=[['Ира: -5', "Player('Ира', -5)", 'Ира: -5']],
    description='отрицательные очки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg08_lines(rows):
    ...
