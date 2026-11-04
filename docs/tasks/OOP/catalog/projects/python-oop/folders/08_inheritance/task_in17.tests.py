from ego.testing import case, rules

@rules(
    require_classes=['Status', 'Created', 'Paid', 'Shipped'],
    require_methods={'Status': ['label', 'can_cancel', 'describe'], 'Created': ['label', 'can_cancel'], 'Paid': ['label', 'can_cancel'], 'Shipped': ['label', 'can_cancel']},
)
@case(
    args=([['new', 'Created'], ['label'], ['can_cancel'], ['describe']],),
    expected=['ok', 'создан', True, 'создан, отмена: да'],
    description='создан',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Shipped'], ['label'], ['can_cancel'], ['describe']],),
    expected=['ok', 'отправлен', False, 'отправлен, отмена: нет'],
    description='отправлен',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Status']],),
    expected=[['error', 'TypeError']],
    description='абстрактный класс создать нельзя',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Paid'], ['is', 'Status'], ['new', 'Status'], ['label']],),
    expected=['ok', True, ['error', 'TypeError'], 'оплачен'],
    description='после неудачного new объект прежний',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Half']],),
    expected=[['error', 'TypeError']],
    description='метод can_cancel остался абстрактным',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Paid'], ['describe'], ['new', 'Shipped'], ['describe'], ['is', 'Paid']],),
    expected=['ok', 'оплачен, отмена: да', 'ok', 'отправлен, отмена: нет', False],
    description='две подряд',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in17_status(actions):
    ...
