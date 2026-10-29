from ego.testing import case, rules

@rules(
    require_classes=['OrderLine'],
    require_decorators={'OrderLine': ['dataclass']},
    require_methods={'OrderLine': ['total']},
)
@case(
    args=([['new', 'Чай', 50], ['total'], ['get', 'count']],),
    expected=['ok', 50, 1],
    description='количество по умолчанию равно 1',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Кофе', 120, 3], ['total']],),
    expected=['ok', 360],
    description='количество передали',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Сок', 80, 2], ['get', 'count'], ['get', 'product']],),
    expected=['ok', 2, 'Сок'],
    description='поля читаются',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Чай', 50], ['set', 'count', 4], ['total']],),
    expected=['ok', 'ok', 200],
    description='количество можно изменить',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Хлеб', 40, 0], ['total']],),
    expected=['ok', 0],
    description='нулевое количество',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Соль', 15], ['new', 'Сахар', 30, 5], ['total'], ['get', 'count']],),
    expected=['ok', 'ok', 150, 5],
    description='второй объект не помнит первый',
    level='full',
    comparison='value',
)
def task_dc07_line(actions):
    ...
