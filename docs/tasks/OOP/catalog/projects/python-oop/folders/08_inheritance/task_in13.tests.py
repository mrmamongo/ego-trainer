from ego.testing import case, rules

@rules(
    require_classes=['Payment', 'Card', 'Cash', 'Crypto'],
    require_bases={'Card': ['Payment'], 'Cash': ['Payment'], 'Crypto': ['Payment']},
    require_methods={'Payment': ['fee', 'total'], 'Card': ['fee'], 'Crypto': ['fee']},
)
@case(
    args=([['new', 'Card'], ['fee', 500], ['total', 500], ['get', 'name']],),
    expected=['ok', 10, 510, 'карта'],
    description='карта берёт 2 процента',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Cash'], ['fee', 500], ['total', 500], ['get', 'name']],),
    expected=['ok', 0, 500, 'наличные'],
    description='наличные без комиссии',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Crypto'], ['fee', 1000], ['total', 1000]],),
    expected=['ok', 11, 1011],
    description='крипта: 1 плюс процент',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Payment'], ['total', 70], ['get', 'name']],),
    expected=['ok', 70, 'платёж'],
    description='базовый платёж',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Card'], ['total', 0], ['fee', 49]],),
    expected=['ok', 0, 0],
    description='нулевая и маленькая суммы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Crypto'], ['total', 0], ['fee', 99], ['fee', 100]],),
    expected=['ok', 1, 1, 2],
    description='граница процента крипты',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Cash'], ['is', 'Payment'], ['get', 'name']],),
    expected=['ok', True, 'наличные'],
    description='Cash тоже Payment',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Card'], ['is', 'Cash'], ['is', 'Payment']],),
    expected=['ok', False, True],
    description='Card не Cash',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in13_payments(actions):
    ...
