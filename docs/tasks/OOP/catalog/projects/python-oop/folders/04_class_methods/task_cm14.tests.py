from ego.testing import case, rules

@rules(
    require_classes=['Ticket'],
    require_methods={'Ticket': ['__init__', 'describe']},
)
@case(
    args=([['new', 'Баг'], ['get', 'id'], ['get', 'next_id']],),
    expected=['ok', 1, 2],
    description='первая заявка получает номер 1',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Баг'], ['new', 'Идея'], ['get', 'id'], ['get', 'next_id']],),
    expected=['ok', 'ok', 2, 3],
    description='вторая заявка получает номер 2',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Баг'], ['describe']],),
    expected=['ok', '№1: Баг'],
    description='описание с номером',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'а'], ['new', 'б'], ['new', 'в'], ['describe'], ['get', 'next_id']],),
    expected=['ok', 'ok', 'ok', '№3: в', 4],
    description='три заявки подряд',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Баг'], ['get', 'id'], ['get', 'id'], ['get', 'title']],),
    expected=['ok', 1, 1, 'Баг'],
    description='номер выдаётся один раз и не меняется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Фича'], ['get', 'id']],),
    expected=['ok', 1],
    description='новая проверка снова начинает с 1',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm14_tickets(actions):
    ...
