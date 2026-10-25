from ego.testing import case, rules

# --- старые случаи: ответы не меняются ---

@case(
    args=({"items": [{"name": "чай", "qty": 2}], "budget": 300},),
    expected="ok",
    description='старое: правильный заказ',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [], "budget": 100},),
    expected="no_items",
    description='старое: пустой заказ',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "кофе", "qty": 3}], "budget": 300},),
    expected="over_budget",
    description='старое: дороже бюджета',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "суп", "qty": 1}, {"name": "чай", "qty": -1}], "budget": 500},),
    expected="bad_qty",
    description='старое: bad_qty важнее unknown_item',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "чай", "qty": 1}, {"name": "булка", "qty": 1}], "budget": 120},),
    expected="ok",
    description='старое: разные товары — не повтор, ровно по бюджету',
    level="full",
    check_inputs_unchanged=True,
)

# --- новое правило: duplicate_item сразу после no_items ---

@case(
    args=({"items": [{"name": "чай", "qty": 1}, {"name": "чай", "qty": 2}], "budget": 500},),
    expected="duplicate_item",
    description='новое: чай записан дважды',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "кофе", "qty": 1}, {"name": "чай", "qty": 1}, {"name": "кофе", "qty": 1}], "budget": 500},),
    expected="duplicate_item",
    description='новое: повтор не рядом',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"items": [{"name": "чай", "qty": 0}, {"name": "чай", "qty": 1}], "budget": 500},),
    expected="duplicate_item",
    description='повтор важнее bad_qty',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)

@case(
    args=({"items": [{"name": "суп", "qty": 1}, {"name": "суп", "qty": 1}], "budget": 500},),
    expected="duplicate_item",
    description='повтор важнее unknown_item',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)

@case(
    args=({"items": [{"name": "чай", "qty": 5}, {"name": "чай", "qty": 5}], "budget": 1},),
    expected="duplicate_item",
    description='повтор важнее over_budget',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)


@rules(
    forbid_nodes=["Try"],
    messages={"Try": "здесь исключения не нужны: проверяй условиями if … return"},
)

def task_er09_validate_order(order):
    ...
