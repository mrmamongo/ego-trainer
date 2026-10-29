from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_methods={'Player': ['__init__', 'describe']},
)
@case(
    args=([['new', 'Аня', 30], ['get', 'hp'], ['get', 'name']],),
    expected=['ok', 30, 'Аня'],
    description='поля сохраняются',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 5], ['describe']],),
    expected=['ok', 'Боря: 5'],
    description='describe собирает строку',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 0], ['get', 'hp']],),
    expected=['ok', 0],
    description='нулевое здоровье',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 100], ['describe'], ['set', 'name', 'Георгий'], ['describe']],),
    expected=['ok', 'Юра: 100', 'ok', 'Георгий: 100'],
    description='после смены имени',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 7], ['set', 'hp', 3], ['get', 'hp'], ['describe']],),
    expected=['ok', 'ok', 3, 'Ира: 3'],
    description='после смены hp',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl03_player(actions):
    ...
