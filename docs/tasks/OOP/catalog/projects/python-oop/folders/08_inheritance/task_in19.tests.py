from ego.testing import case, rules

@rules(
    require_classes=['Discount', 'Percent'],
    require_bases={'Percent': ['Discount']},
    require_methods={'Discount': ['apply'], 'Percent': ['__init__', 'apply']},
)
@case(
    args=([['new', 'Percent', 10], ['apply', 200]],),
    expected=['ok', 180],
    description='старое: проценты',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Discount'], ['apply', 100]],),
    expected=['ok', 100],
    description='старое: без скидки',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Fixed', 30], ['apply', 100], ['label']],),
    expected=['ok', 70, '-30'],
    description='новое: фиксированная скидка',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Percent', 25], ['label'], ['apply', 80]],),
    expected=['ok', '-25%', 60],
    description='подпись процента',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Discount'], ['label']],),
    expected=['ok', 'без скидки'],
    description='подпись базовой скидки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Fixed', 500], ['apply', 100], ['is', 'Discount']],),
    expected=['ok', 0, True],
    description='цена не уходит в минус',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Fixed', 0], ['apply', 0], ['label']],),
    expected=['ok', 0, '-0'],
    description='нулевая фиксированная',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Percent', 100], ['apply', 50], ['label']],),
    expected=['ok', 0, '-100%'],
    description='сто процентов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in19_discounts(actions):
    ...
