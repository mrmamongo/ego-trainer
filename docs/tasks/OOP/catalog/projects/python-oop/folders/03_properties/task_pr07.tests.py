from ego.testing import case, rules

@rules(
    require_classes=['Profile'],
    require_decorators={'Profile.email': ['property']},
)
@case(
    args=([['new', 'Аня', 'anya@mail.ru'], ['get', 'email']],),
    expected=['ok', 'anya@mail.ru'],
    description='обычный адрес',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', '  boris@mail.ru  '], ['get', 'email']],),
    expected=['ok', 'boris@mail.ru'],
    description='пробелы по краям убираются',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 'vika.mail.ru'], ['new', 'Вика', 'vika@mail.ru'], ['get', 'name']],),
    expected=[['error', 'ValueError', 'в email нужна @'], 'ok', 'Вика'],
    description='без @ объект не создаётся',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 'yura@x.org'], ['set', 'email', 'yura2@x.org '], ['get', 'email']],),
    expected=['ok', 'ok', 'yura2@x.org'],
    description='новое значение через сеттер',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 'ira@x.org'], ['set', 'email', 'ira'], ['get', 'email']],),
    expected=['ok', ['error', 'ValueError', 'в email нужна @'], 'ira@x.org'],
    description='плохой адрес отклонён, старый остался',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Лев', 'lev@x.org'], ['set', 'email', ''], ['get', 'email']],),
    expected=['ok', ['error', 'ValueError', 'в email нужна @'], 'lev@x.org'],
    description='пустая строка',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr07_profile(actions):
    ...
