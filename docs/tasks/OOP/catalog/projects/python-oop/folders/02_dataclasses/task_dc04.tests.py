from ego.testing import case, rules

@rules(
    require_classes=['ChatMessage'],
    require_decorators={'ChatMessage': ['dataclass']},
    require_methods={'ChatMessage': ['react']},
)
@case(
    args=([['new', 'Аня', 'привет'], ['react', 'ок'], ['react', 'огонь'], ['get', 'reactions']],),
    expected=['ok', 1, 2, ['ок', 'огонь']],
    description='реакции копятся в сообщении',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Боря', 'всем привет'], ['get', 'reactions']],),
    expected=['ok', []],
    description='у нового сообщения реакций нет',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Аня', 'привет'], ['react', 'ок'], ['new', 'Боря', 'пока'], ['get', 'reactions'], ['react', 'огонь']],),
    expected=['ok', 1, 'ok', [], 1],
    description='у второго сообщения свой список реакций',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Вика', 'раз', ['ок']], ['react', 'огонь'], ['get', 'reactions']],),
    expected=['ok', 2, ['ок', 'огонь']],
    description='реакции можно передать при создании',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Аня', 'привет'], ['get', 'author'], ['get', 'text']],),
    expected=['ok', 'Аня', 'привет'],
    description='поля author и text на месте',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'А', '1'], ['react', 'x'], ['new', 'Б', '2'], ['react', 'y'], ['new', 'В', '3'], ['get', 'reactions']],),
    expected=['ok', 1, 'ok', 1, 'ok', []],
    description='три сообщения подряд не делят список',
    level='full',
    comparison='value',
)
def task_dc04_message(actions):
    ...
