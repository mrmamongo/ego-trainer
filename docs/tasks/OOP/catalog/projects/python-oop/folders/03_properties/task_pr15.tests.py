from ego.testing import case, rules

@rules(
    require_classes=['Profile'],
    require_decorators={'Profile.email': ['property'], 'Profile.username': ['property']},
    require_methods={'Profile': ['__init__']},
    forbid_attributes_outside_class=['_email'],
)
@case(
    args=([['new', 'Аня', 'anya@mail.ru'], ['get', 'email'], ['get', 'username']],),
    expected=['ok', 'anya@mail.ru', 'anya'],
    description='обычный адрес',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', '  Boris@Mail.RU '], ['get', 'email'], ['get', 'username']],),
    expected=['ok', 'boris@mail.ru', 'boris'],
    description='пробелы и заглавные буквы убираются',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 'vika.mail.ru'], ['new', 'Вика', 'vika@mail.ru'], ['get', 'name']],),
    expected=[['error', 'ValueError', 'некорректный email'], 'ok', 'Вика'],
    description='без @ объект не создаётся',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 'yura@x.org'], ['set', 'email', 'Yura2@X.org'], ['get', 'username']],),
    expected=['ok', 'ok', 'yura2'],
    description='username следует за email',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 'ira@x.org'], ['set', 'email', '@x.org'], ['set', 'email', 'ira@'], ['get', 'email']],),
    expected=['ok', ['error', 'ValueError', 'некорректный email'], ['error', 'ValueError', 'некорректный email'], 'ira@x.org'],
    description='@ в начале и в конце отклоняется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Лев', 'lev@x.org'], ['set', 'email', '  '], ['get', 'email']],),
    expected=['ok', ['error', 'ValueError', 'некорректный email'], 'lev@x.org'],
    description='пустая строка',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Мия', 'mia@x.org'], ['set', 'username', 'nina'], ['get', 'username']],),
    expected=['ok', ['error', 'AttributeError', ''], 'mia'],
    description='username только для чтения',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Паша', 'a@b'], ['get', 'username']],),
    expected=['ok', 'a'],
    description='самый короткий допустимый адрес',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr15_profile(actions):
    ...
