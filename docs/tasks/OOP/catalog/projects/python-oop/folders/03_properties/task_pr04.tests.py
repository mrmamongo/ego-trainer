from ego.testing import case, rules

@rules(
    require_classes=['Product'],
    require_decorators={'Product.final_price': ['property']},
)
@case(
    args=([['new', 200, 10], ['get', 'final_price']],),
    expected=['ok', 180],
    description='скидка 10 процентов',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 500, 0], ['get', 'final_price']],),
    expected=['ok', 500],
    description='без скидки',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 80, 50], ['get', 'final_price'], ['get', 'price']],),
    expected=['ok', 40, 80],
    description='половина цены, цена не меняется',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 150, 15], ['get', 'final_price']],),
    expected=['ok', 127],
    description='дробная часть отбрасывается',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 999, 100], ['get', 'final_price']],),
    expected=['ok', 0],
    description='скидка сто процентов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 33, 50], ['get', 'final_price']],),
    expected=['ok', 16],
    description='нечётная цена',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 0, 20], ['get', 'final_price']],),
    expected=['ok', 0],
    description='нулевая цена',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr04_price(actions):
    ...
