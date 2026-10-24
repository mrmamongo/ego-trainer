from ego.testing import case


@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"},
        1,
        2,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 86, 2: 13}, "bags": {1: {"ore": 2}, 2: {}}, "treasury": 1},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 3,
            "status": "open",
        },
        "receipt": {"quantity": 2, "gross": 14, "fee": 1},
        "reason": None,
    },
    description="Частичная покупка оплачивает только запрос и оставляет лот открытым",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"},
        1,
        5,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 65, 2: 32}, "bags": {1: {"ore": 5}, 2: {}}, "treasury": 3},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 0,
            "status": "closed",
        },
        "receipt": {"quantity": 5, "gross": 35, "fee": 3},
        "reason": None,
    },
    description="Полный выкуп сохраняет старое поведение",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"},
        1,
        0,
    ),
    expected={
        "status": "rejected",
        "accounts": {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 5,
            "status": "open",
        },
        "receipt": None,
        "reason": "invalid_quantity",
    },
    description="Нулевой запрос не выполняет старый полный выкуп",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 0, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "closed"},
        1,
        -2,
    ),
    expected={
        "status": "rejected",
        "accounts": {"gold": {1: 0, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 5,
            "status": "closed",
        },
        "receipt": None,
        "reason": "invalid_quantity",
    },
    description="Отрицательный запрос проверяется раньше закрытия и денег",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 0, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "closed"},
        1,
        6,
    ),
    expected={
        "status": "rejected",
        "accounts": {"gold": {1: 0, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 5,
            "status": "closed",
        },
        "receipt": None,
        "reason": "lot_closed",
    },
    description="Закрытие проверяется раньше недостаточного запаса",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 0, "status": "open"},
        1,
        1,
    ),
    expected={
        "status": "rejected",
        "accounts": {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 0,
            "status": "open",
        },
        "receipt": None,
        "reason": "lot_closed",
    },
    description="Пустой открытый лот недоступен",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 0, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"},
        1,
        6,
    ),
    expected={
        "status": "rejected",
        "accounts": {"gold": {1: 0, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 5,
            "status": "open",
        },
        "receipt": None,
        "reason": "not_enough_items",
    },
    description="Нехватка товара проверяется раньше денег",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 13, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"},
        1,
        2,
    ),
    expected={
        "status": "rejected",
        "accounts": {"gold": {1: 13, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 5,
            "status": "open",
        },
        "receipt": None,
        "reason": "not_enough_gold",
    },
    description="Частичный запрос не исполняется при нехватке одной монеты",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 14, 2: 0}, "bags": {1: {"ore": 3}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"},
        1,
        2,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 0, 2: 13}, "bags": {1: {"ore": 5}, 2: {}}, "treasury": 1},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 3,
            "status": "open",
        },
        "receipt": {"quantity": 2, "gross": 14, "fee": 1},
        "reason": None,
    },
    description="Денег хватает на часть, хотя полный лот дороже; сумка пополняется",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"},
        1,
        2,
        100,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 86, 2: 0}, "bags": {1: {"ore": 2}, 2: {}}, "treasury": 14},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 3,
            "status": "open",
        },
        "receipt": {"quantity": 2, "gross": 14, "fee": 14},
        "reason": None,
    },
    description="Стопроцентная комиссия применяется к купленной части",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"},
        1,
        4,
        0,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 72, 2: 28}, "bags": {1: {"ore": 4}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 1,
            "status": "open",
        },
        "receipt": {"quantity": 4, "gross": 28, "fee": 0},
        "reason": None,
    },
    description="Нулевая комиссия и остаток в одну единицу",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"},
        1,
        3,
        33,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 79, 2: 15}, "bags": {1: {"ore": 3}, 2: {}}, "treasury": 6},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 2,
            "status": "open",
        },
        "receipt": {"quantity": 3, "gross": 21, "fee": 6},
        "reason": None,
    },
    description="Нестандартная комиссия округляется от стоимости купленной части",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla20_buy_quantity(accounts, lot, buyer_id, quantity, fee_percent=10): ...
