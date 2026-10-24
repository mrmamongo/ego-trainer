from ego.testing import case


@case(
    args=(
        {"iron": 2, "wood": 0},
        {"ingredients": {"iron": 1, "wood": 1}, "product": {"item": "handle", "qty": 1}},
    ),
    expected={"status": "rejected", "inventory": {"iron": 2, "wood": 0}, "missing_item": "wood"},
    description="Поздняя нехватка не списывает уже проверенное железо",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 2, "wood": 1},
        {"ingredients": {"iron": 1, "wood": 1}, "product": {"item": "handle", "qty": 1}},
    ),
    expected={
        "status": "crafted",
        "inventory": {"iron": 1, "wood": 0, "handle": 1},
        "missing_item": None,
    },
    description="Успех списывает все материалы и добавляет продукт",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"zinc": 0, "apple": 0},
        {"ingredients": {"zinc": 2, "apple": 1}, "product": {"item": "mix", "qty": 1}},
    ),
    expected={"status": "rejected", "inventory": {"zinc": 0, "apple": 0}, "missing_item": "apple"},
    description="При нескольких нехватках возвращается первая по алфавиту, а не по порядку рецепта",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, {"ingredients": {}, "product": {"item": "gift", "qty": 2}}),
    expected={"status": "crafted", "inventory": {"gift": 2}, "missing_item": None},
    description="Пустой набор ингредиентов позволяет создать продукт",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"coin": 7}, {"ingredients": {"iron": 1}, "product": {"item": "nail", "qty": 1}}),
    expected={"status": "rejected", "inventory": {"coin": 7}, "missing_item": "iron"},
    description="Отсутствующий материал не добавляется нулевым ключом при отказе",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 3, "nail": 4},
        {"ingredients": {"iron": 2}, "product": {"item": "nail", "qty": 3}},
    ),
    expected={"status": "crafted", "inventory": {"iron": 1, "nail": 7}, "missing_item": None},
    description="Количество продукта добавляется к существующему запасу",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"iron": 3}, {"ingredients": {"iron": 2}, "product": {"item": "iron", "qty": 4}}),
    expected={"status": "crafted", "inventory": {"iron": 5}, "missing_item": None},
    description="Для совпадающих материала и продукта сначала идёт списание, затем добавление",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"a": 5, "b": 3, "c": 0, "coin": 7},
        {"ingredients": {"c": 1, "b": 2, "a": 4}, "product": {"item": "result", "qty": 1}},
    ),
    expected={
        "status": "rejected",
        "inventory": {"a": 5, "b": 3, "c": 0, "coin": 7},
        "missing_item": "c",
    },
    description="Несколько успешных проверок до отказа не вызывают частичной потери ресурсов",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"wood": 1, "gem": 0, "coin": 7},
        {"ingredients": {"wood": 1}, "product": {"item": "stick", "qty": 2}},
    ),
    expected={
        "status": "crafted",
        "inventory": {"wood": 0, "gem": 0, "coin": 7, "stick": 2},
        "missing_item": None,
    },
    description="Нулевые и посторонние ключи сохраняются после успеха",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"wood": 2, "iron": 1},
        {"ingredients": {"wood": 2, "iron": 1}, "product": {"item": "hammer", "qty": 2}},
    ),
    expected={
        "status": "crafted",
        "inventory": {"wood": 0, "iron": 0, "hammer": 2},
        "missing_item": None,
    },
    description="Точный запас нескольких материалов достаточен и сохраняет нулевые остатки",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_xla18_craft_atomic(inventory, recipe): ...
