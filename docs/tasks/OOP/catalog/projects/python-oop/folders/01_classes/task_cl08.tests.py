from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_methods={'Player': ['__init__', 'heal']},
)
@case(
    args=([['new', 'Аня', 30], ['heal', 10], ['get', 'hp']],),
    expected=['ok', 40, 40],
    description='здоровье сохраняется',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 1], ['heal', 5]],),
    expected=['ok', 6],
    description='возвращается новое здоровье',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 0], ['heal', 0], ['get', 'hp']],),
    expected=['ok', 0, 0],
    description='ноль плюс ноль',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 10], ['heal', 5], ['heal', 5], ['get', 'hp']],),
    expected=['ok', 15, 20, 20],
    description='лечим дважды',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 50], ['heal', 1], ['get', 'name']],),
    expected=['ok', 51, 'Ира'],
    description='имя не трогаем',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl08_heal(actions):
    ...
