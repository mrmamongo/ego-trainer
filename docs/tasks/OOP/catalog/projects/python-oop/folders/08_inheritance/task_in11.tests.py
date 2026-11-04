from ego.testing import case, rules

@rules(
    require_classes=['Notification', 'Email', 'Sms', 'Push'],
    require_bases={'Email': ['Notification'], 'Sms': ['Notification'], 'Push': ['Notification']},
    require_methods={'Notification': ['__init__', 'format', 'send'], 'Email': ['format'], 'Sms': ['format'], 'Push': ['format']},
)
@case(
    args=([['new', 'Email', 'a@x.ru'], ['send', 'Привет']],),
    expected=['ok', 'a@x.ru: Письмо: Привет'],
    description='письмо',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Sms', '+7900'], ['send', 'Очень длинное сообщение']],),
    expected=['ok', '+7900: Очень длин'],
    description='sms обрезается до 10 символов',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Push', 'app'], ['send', 'новый заказ']],),
    expected=['ok', 'app: НОВЫЙ ЗАКАЗ'],
    description='push большими буквами',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Notification', 'лог'], ['send', 'как есть']],),
    expected=['ok', 'лог: как есть'],
    description='базовый класс',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Email', 'b@x.ru'], ['send', 'раз'], ['send', 'два'], ['get', 'sent']],),
    expected=['ok', 'b@x.ru: Письмо: раз', 'b@x.ru: Письмо: два', 2],
    description='счётчик отправок',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Sms', '+7911'], ['send', 'коротко'], ['get', 'to'], ['is', 'Notification']],),
    expected=['ok', '+7911: коротко', '+7911', True],
    description='короткий текст и isinstance',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Push', 'app'], ['get', 'sent'], ['send', ''], ['get', 'sent']],),
    expected=['ok', 0, 'app: ', 1],
    description='пустой текст тоже отправка',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Sms', '+7'], ['send', 'ровно десять'], ['send', '1234567890']],),
    expected=['ok', '+7: ровно деся', '+7: 1234567890'],
    description='граница 10 символов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in11_notify(actions):
    ...
