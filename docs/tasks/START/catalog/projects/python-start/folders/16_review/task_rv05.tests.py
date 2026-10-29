from ego.testing import case, rules

@case(
    args=([{'customer': 'Аня', 'total': 100}, {'customer': 'Боря', 'total': 50}, {'customer': 'Аня', 'total': 30}],),
    expected={'Аня': 130, 'Боря': 50},
    description='два клиента',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'customer': 'Вика', 'total': 10}],),
    expected={'Вика': 10},
    description='один заказ',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'customer': 'Боря', 'total': 5}, {'customer': 'Аня', 'total': 7}, {'customer': 'Боря', 'total': 5}],),
    expected={'Боря': 10, 'Аня': 7},
    description='порядок по первому появлению',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([],),
    expected={},
    description='нет заказов',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'customer': 'Яна', 'total': 0}],),
    expected={'Яна': 0},
    description='клиент с нулевой суммой остаётся',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'customer': 'Яна', 'total': 3}, {'customer': 'Аня', 'total': 4}, {'customer': 'Яна', 'total': 1}, {'customer': 'Аня', 'total': 2}],),
    expected={'Яна': 4, 'Аня': 6},
    description='обратный алфавитный порядок',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'customer': 'Аня', 'total': 1}, {'customer': 'Аня', 'total': 2}, {'customer': 'Аня', 'total': 3}],),
    expected={'Аня': 6},
    description='один клиент много заказов',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@rules(forbid_imports=["collections"])

def task_rv05_totals_by_customer(orders):
    ...
