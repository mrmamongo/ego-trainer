from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_methods={'Player': ['__init__', '__lt__']},
)
@case(
    args=([['Аня', 100], ['Боря', 150], ['Вика', 100]],),
    expected=['Боря', 'Аня', 'Вика'],
    description='лидер, потом ничья по имени',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Вика', 50], ['Аня', 50]],),
    expected=['Аня', 'Вика'],
    description='ничья: по алфавиту',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 10]],),
    expected=['Аня'],
    description='один игрок',
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
    args=([['Гена', 0], ['Боря', 0], ['Аня', 0]],),
    expected=['Аня', 'Боря', 'Гена'],
    description='у всех ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', -5], ['Боря', -10]],),
    expected=['Аня', 'Боря'],
    description='отрицательные очки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Ира', 70], ['Аня', 90], ['Боря', 70], ['Вика', 90]],),
    expected=['Аня', 'Вика', 'Боря', 'Ира'],
    description='две ничьи',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg14_board(rows):
    ...
