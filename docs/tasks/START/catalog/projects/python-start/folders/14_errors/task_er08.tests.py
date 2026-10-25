from ego.testing import case, rules

@case(
    args=({"items": [{"name": "чай", "qty": 2}], "budget": 300},),
    expected="ok",
    description='правильный заказ',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [], "budget": 100},),
    expected="no_items",
    description='пустой заказ',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "кофе", "qty": 0}], "budget": 500},),
    expected="bad_qty",
    description='нулевое количество',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "кофе", "qty": 3}], "budget": 300},),
    expected="over_budget",
    description='дороже бюджета (360 > 300)',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "суп", "qty": 1}], "budget": 500},),
    expected="unknown_item",
    description='товара нет в ценнике',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "чай", "qty": 2}, {"name": "булка", "qty": 1}], "budget": 170},),
    expected="ok",
    description='ровно по бюджету (100 + 70)',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "чай", "qty": "2"}], "budget": 500},),
    expected="bad_qty",
    description='количество — строка',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "суп", "qty": 1}, {"name": "чай", "qty": -1}], "budget": 500},),
    expected="bad_qty",
    description='bad_qty важнее unknown_item, даже если неизвестный товар раньше в списке',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)

@case(
    args=({"items": [{"name": "суп", "qty": 5}], "budget": 1},),
    expected="unknown_item",
    description='unknown_item важнее over_budget',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)

@case(
    args=({"items": [], "budget": 0},),
    expected="no_items",
    description='пустой заказ и нулевой бюджет',
    level="full",
    check_inputs_unchanged=True,
)


@rules(
    forbid_nodes=["Try"],
    messages={"Try": "здесь исключения не нужны: проверяй условиями if … return"},
)

def task_er08_validate_order(order):
    ...
