from ego.testing import case, rules

@rules(
    require_classes=['Quest'],
    require_decorators={'Quest': ['dataclass']},
    require_methods={'Quest': ['summary', 'finish']},
)
@case(
    args=([['new', 'Волки', 100], ['summary']],),
    expected=['ok', 'Волки: 100'],
    description='старое поведение: описание нового квеста',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Волки', 100], ['finish'], ['summary'], ['get', 'done']],),
    expected=['ok', 100, 'Волки: 100 (готово)', True],
    description='выполнение квеста',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Лис', 50], ['get', 'done']],),
    expected=['ok', False],
    description='новый квест не выполнен',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Лис', 50], ['finish'], ['finish']],),
    expected=['ok', 50, ['error', 'ValueError', 'квест уже выполнен']],
    description='второй finish — ошибка',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Тролль', 70, True], ['summary']],),
    expected=['ok', 'Тролль: 70 (готово)'],
    description='квест можно создать уже выполненным',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Дракон', 0], ['summary'], ['get', 'reward']],),
    expected=['ok', 'Дракон: 0', 0],
    description='старый случай: нулевая награда',
    level='full',
    comparison='value',
)
def task_dc15_quest(actions):
    ...
