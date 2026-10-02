from ego.testing import case


@case(
    args=(
        {"iron": 2, "hammer": 1, "gem": 0},
        {
            "ingredients": {"iron": 2},
            "tools": {"hammer": 1},
            "product": {"item": "sword", "qty": 1},
        },
    ),
    expected={
        "status": "crafted",
        "inventory": {"iron": 0, "hammer": 1, "gem": 0, "sword": 1},
        "missing": {},
    },
    description="Крафт расходует материалы, сохраняет инструмент и нулевой ключ",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 2},
        {
            "ingredients": {"iron": 2},
            "tools": {"hammer": 1},
            "product": {"item": "sword", "qty": 1},
        },
    ),
    expected={"status": "missing", "inventory": {"iron": 2}, "missing": {"hammer": 1}},
    description="Отсутствие инструмента отклоняет крафт без списания материалов",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 2},
        {"ingredients": {"iron": 2}, "tools": {"iron": 1}, "product": {"item": "sword", "qty": 1}},
    ),
    expected={"status": "missing", "inventory": {"iron": 2}, "missing": {"iron": 1}},
    description="Материал и инструмент одного имени требуют суммарного запаса",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 3},
        {"ingredients": {"iron": 2}, "tools": {"iron": 1}, "product": {"item": "sword", "qty": 1}},
    ),
    expected={"status": "crafted", "inventory": {"iron": 1, "sword": 1}, "missing": {}},
    description="При точном суммарном запасе списывается только материал",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"wood": 3, "board": 4, "coin": 8},
        {"ingredients": {"wood": 2}, "product": {"item": "board", "qty": 3}},
    ),
    expected={"status": "crafted", "inventory": {"wood": 1, "board": 7, "coin": 8}, "missing": {}},
    description="Рецепт без tools сохраняет прежнее поведение и добавляет к имеющемуся продукту",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"zinc": 1, "iron": 0, "hammer": 0, "coin": 9},
        {
            "ingredients": {"zinc": 3, "iron": 2},
            "tools": {"saw": 1, "hammer": 2},
            "product": {"item": "armor", "qty": 1},
        },
    ),
    expected={
        "status": "missing",
        "inventory": {"zinc": 1, "iron": 0, "hammer": 0, "coin": 9},
        "missing": {"hammer": 2, "iron": 2, "saw": 1, "zinc": 2},
    },
    description="Нехватки всех материалов и инструментов собираются до списания",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 1, "hammer": 1, "gem": 0},
        {
            "ingredients": {"iron": 2},
            "tools": {"hammer": 1},
            "product": {"item": "sword", "qty": 1},
        },
    ),
    expected={
        "status": "missing",
        "inventory": {"iron": 1, "hammer": 1, "gem": 0},
        "missing": {"iron": 1},
    },
    description="Наличие инструмента не отменяет нехватку материала",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, {"ingredients": {}, "tools": {}, "product": {"item": "gift", "qty": 2}}),
    expected={"status": "crafted", "inventory": {"gift": 2}, "missing": {}},
    description="Пустые требования позволяют создать продукт из пустого инвентаря",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"iron": 3},
        {"ingredients": {"iron": 2}, "tools": {"iron": 1}, "product": {"item": "iron", "qty": 4}},
    ),
    expected={"status": "crafted", "inventory": {"iron": 5}, "missing": {}},
    description="Один предмет может быть материалом, инструментом и продуктом",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"ore": 1, "zero": 0, "coin": 7},
        {"ingredients": {"ore": 1}, "tools": {}, "product": {"item": "ingot", "qty": 2}},
    ),
    expected={
        "status": "crafted",
        "inventory": {"ore": 0, "zero": 0, "coin": 7, "ingot": 2},
        "missing": {},
    },
    description="Явно пустые tools не меняют обычный крафт и сохранение ключей",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_xla16_craft(inventory, recipe): ...
