from ego.testing import case


@case(
    args=(
        {"iron": 2},
        [
            {"id": "A", "recipe_id": "nail"},
            {"id": "B", "recipe_id": "unknown"},
            {"id": "C", "recipe_id": "plate"},
        ],
        {
            "nail": {"ingredients": {"iron": 1}, "product": {"item": "nail", "qty": 1}},
            "plate": {"ingredients": {"iron": 2}, "product": {"item": "plate", "qty": 1}},
        },
    ),
    expected={
        "inventory": {"iron": 1, "nail": 1},
        "orders": [
            {"id": "A", "status": "crafted", "reason": None, "missing": {}},
            {"id": "B", "status": "rejected", "reason": "unknown_recipe", "missing": {}},
            {
                "id": "C",
                "status": "rejected",
                "reason": "missing_resources",
                "missing": {"iron": 1},
            },
        ],
        "crafted_count": 1,
    },
    description="Успех, неизвестный рецепт и нехватка сохраняются в порядке заказов",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"ore": 2},
        [{"id": "smelt", "recipe_id": "ingot"}, {"id": "forge", "recipe_id": "blade"}],
        {
            "ingot": {"ingredients": {"ore": 2}, "product": {"item": "iron", "qty": 3}},
            "blade": {"ingredients": {"iron": 2}, "product": {"item": "blade", "qty": 1}},
        },
    ),
    expected={
        "inventory": {"ore": 0, "iron": 1, "blade": 1},
        "orders": [
            {"id": "smelt", "status": "crafted", "reason": None, "missing": {}},
            {"id": "forge", "status": "crafted", "reason": None, "missing": {}},
        ],
        "crafted_count": 2,
    },
    description="Следующий заказ использует продукт предыдущего",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 1},
        [{"id": "large", "recipe_id": "plate"}, {"id": "small", "recipe_id": "nail"}],
        {
            "nail": {"ingredients": {"iron": 1}, "product": {"item": "nail", "qty": 1}},
            "plate": {"ingredients": {"iron": 2}, "product": {"item": "plate", "qty": 1}},
        },
    ),
    expected={
        "inventory": {"iron": 0, "nail": 1},
        "orders": [
            {
                "id": "large",
                "status": "rejected",
                "reason": "missing_resources",
                "missing": {"iron": 1},
            },
            {"id": "small", "status": "crafted", "reason": None, "missing": {}},
        ],
        "crafted_count": 1,
    },
    description="Отказ первого заказа не останавливает следующий",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 1, "gem": 0},
        [],
        {
            "nail": {"ingredients": {"iron": 1}, "product": {"item": "nail", "qty": 1}},
            "plate": {"ingredients": {"iron": 2}, "product": {"item": "plate", "qty": 1}},
        },
    ),
    expected={"inventory": {"iron": 1, "gem": 0}, "orders": [], "crafted_count": 0},
    description="Пустая очередь возвращает новый снимок начального инвентаря",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, [{"id": "B", "recipe_id": "x"}, {"id": "A", "recipe_id": "x"}], {}),
    expected={
        "inventory": {},
        "orders": [
            {"id": "B", "status": "rejected", "reason": "unknown_recipe", "missing": {}},
            {"id": "A", "status": "rejected", "reason": "unknown_recipe", "missing": {}},
        ],
        "crafted_count": 0,
    },
    description="Пустой каталог отклоняет каждый заказ, сохраняя его исходный порядок",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 1},
        [{"id": "first", "recipe_id": "plate"}, {"id": "second", "recipe_id": "plate"}],
        {
            "nail": {"ingredients": {"iron": 1}, "product": {"item": "nail", "qty": 1}},
            "plate": {"ingredients": {"iron": 2}, "product": {"item": "plate", "qty": 1}},
        },
    ),
    expected={
        "inventory": {"iron": 1},
        "orders": [
            {
                "id": "first",
                "status": "rejected",
                "reason": "missing_resources",
                "missing": {"iron": 1},
            },
            {
                "id": "second",
                "status": "rejected",
                "reason": "missing_resources",
                "missing": {"iron": 1},
            },
        ],
        "crafted_count": 0,
    },
    description="Повторный отказ видит тот же неизменившийся запас",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 4, "hammer": 1},
        [{"id": "one", "recipe_id": "sword"}, {"id": "two", "recipe_id": "sword"}],
        {
            "sword": {
                "ingredients": {"iron": 2},
                "tools": {"hammer": 1},
                "product": {"item": "sword", "qty": 1},
            }
        },
    ),
    expected={
        "inventory": {"iron": 0, "hammer": 1, "sword": 2},
        "orders": [
            {"id": "one", "status": "crafted", "reason": None, "missing": {}},
            {"id": "two", "status": "crafted", "reason": None, "missing": {}},
        ],
        "crafted_count": 2,
    },
    description="Сохранённый инструмент доступен обоим заказам",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 2},
        [{"id": "overlap", "recipe_id": "sword"}, {"id": "simple", "recipe_id": "nail"}],
        {
            "sword": {
                "ingredients": {"iron": 2},
                "tools": {"iron": 1},
                "product": {"item": "sword", "qty": 1},
            },
            "nail": {"ingredients": {"iron": 1}, "product": {"item": "nail", "qty": 1}},
        },
    ),
    expected={
        "inventory": {"iron": 1, "nail": 1},
        "orders": [
            {
                "id": "overlap",
                "status": "rejected",
                "reason": "missing_resources",
                "missing": {"iron": 1},
            },
            {"id": "simple", "status": "crafted", "reason": None, "missing": {}},
        ],
        "crafted_count": 1,
    },
    description="Нехватка суммарных требований не расходует запас следующего заказа",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 2, "nail": 5},
        [
            {"id": "z", "recipe_id": "nail"},
            {"id": "a", "recipe_id": "unknown"},
            {"id": "m", "recipe_id": "nail"},
        ],
        {
            "nail": {"ingredients": {"iron": 1}, "product": {"item": "nail", "qty": 1}},
            "plate": {"ingredients": {"iron": 2}, "product": {"item": "plate", "qty": 1}},
        },
    ),
    expected={
        "inventory": {"iron": 0, "nail": 7},
        "orders": [
            {"id": "z", "status": "crafted", "reason": None, "missing": {}},
            {"id": "a", "status": "rejected", "reason": "unknown_recipe", "missing": {}},
            {"id": "m", "status": "crafted", "reason": None, "missing": {}},
        ],
        "crafted_count": 2,
    },
    description="Неизвестный заказ между успехами не откатывает и не останавливает их",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {},
        [{"id": "gather", "recipe_id": "wood"}, {"id": "build", "recipe_id": "planks"}],
        {
            "wood": {"ingredients": {}, "product": {"item": "wood", "qty": 2}},
            "planks": {"ingredients": {"wood": 2}, "product": {"item": "plank", "qty": 4}},
        },
    ),
    expected={
        "inventory": {"wood": 0, "plank": 4},
        "orders": [
            {"id": "gather", "status": "crafted", "reason": None, "missing": {}},
            {"id": "build", "status": "crafted", "reason": None, "missing": {}},
        ],
        "crafted_count": 2,
    },
    description="Рецепт без материалов может обеспечить следующий заказ",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_xla17_craft_queue(inventory, orders, recipes): ...
