from ego.testing import case, rules

@rules(
    require_classes=['MessageCounter'],
    require_methods={'MessageCounter': ['__init__', 'post', 'is_quiet']},
)
@case(
    args=([['new'], ['is_quiet'], ['post', 'Аня'], ['is_quiet']],),
    expected=['ok', True, None, False],
    description='тишина и первое сообщение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['post', 'Аня'], ['post', 'Боря'], ['get', 'count'], ['get', 'last_author']],),
    expected=['ok', None, None, 2, 'Боря'],
    description='два автора',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['get', 'count'], ['get', 'last_author']],),
    expected=['ok', 0, None],
    description='новый счётчик пуст',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['post', 'А'], ['post', 'А'], ['post', 'А'], ['get', 'count'], ['get', 'last_author']],),
    expected=['ok', None, None, None, 3, 'А'],
    description='один автор три раза',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['post', 'Аня'], ['post', 'Боря'], ['post', 'Аня'], ['get', 'last_author'], ['is_quiet']],),
    expected=['ok', None, None, None, 'Аня', False],
    description='автор возвращается',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl06_chat(actions):
    ...
