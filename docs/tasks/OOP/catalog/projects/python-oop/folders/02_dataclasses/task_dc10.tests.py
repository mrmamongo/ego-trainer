from ego.testing import case, rules

@rules(
    require_classes=['Quest'],
    require_decorators={'Quest': ['dataclass']},
    require_methods={'Quest': ['add_tag', 'has_tag']},
)
@case(
    args=([['new', 'Волки'], ['get', 'reward'], ['add_tag', 'бой'], ['add_tag', 'бой'], ['has_tag', 'бой']],),
    expected=['ok', 10, 1, 1, True],
    description='награда по умолчанию, тег не дублируется',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Лис', 50], ['get', 'reward'], ['has_tag', 'ночь']],),
    expected=['ok', 50, False],
    description='награду передали, тегов нет',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Волки'], ['add_tag', 'бой'], ['new', 'Лис'], ['get', 'tags'], ['has_tag', 'бой']],),
    expected=['ok', 1, 'ok', [], False],
    description='у каждого квеста свой список тегов',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Тролль', 100, ['босс']], ['add_tag', 'огонь'], ['get', 'tags']],),
    expected=['ok', 2, ['босс', 'огонь']],
    description='теги можно передать при создании',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Дракон'], ['add_tag', 'а'], ['add_tag', 'б'], ['add_tag', 'а'], ['get', 'tags']],),
    expected=['ok', 1, 2, 2, ['а', 'б']],
    description='порядок тегов сохраняется',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Крыса', 0], ['get', 'title'], ['get', 'reward'], ['get', 'tags']],),
    expected=['ok', 'Крыса', 0, []],
    description='нулевая награда — это не «не передали»',
    level='full',
    comparison='value',
)
def task_dc10_quest(actions):
    ...
