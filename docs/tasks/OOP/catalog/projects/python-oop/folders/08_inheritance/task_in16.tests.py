from ego.testing import case, rules

@rules(
    require_classes=['Discount', 'Percent', 'Fixed'],
    require_bases={'Percent': ['Discount'], 'Fixed': ['Discount']},
    require_methods={'Discount': ['apply'], 'Percent': ['__init__'], 'Fixed': ['__init__', 'apply']},
)
@case(
    args=([['new', 'Percent', 10], ['apply', 200]],),
    expected=['ok', 180],
    description='десять процентов',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Fixed', 30], ['apply', 100]],),
    expected=['ok', 70],
    description='фиксированная скидка',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Discount'], ['apply', 100]],),
    expected=['ok', 100],
    description='без скидки',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Percent', 50], ['apply', 99], ['apply', 0]],),
    expected=['ok', 50, 0],
    description='половина и граница',
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
    args=([['new', 'Percent', 0], ['apply', 40], ['get', 'percent']],),
    expected=['ok', 40, 0],
    description='нулевой процент',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in16_discount(actions):
    ...
