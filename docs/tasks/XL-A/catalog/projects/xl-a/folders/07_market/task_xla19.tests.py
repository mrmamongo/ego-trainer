from ego.testing import case


@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 10, "quantity": 2, "status": "open"},
        1,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 80, 2: 18}, "bags": {1: {"ore": 2}, 2: {}}, "treasury": 2},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 10,
            "quantity": 0,
            "status": "closed",
        },
        "receipt": {"quantity": 2, "gross": 20, "fee": 2},
        "reason": None,
    },
    description="Комиссия вычитается из выплаты продавцу: золото сохраняется",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"gold": {1: 19, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 10, "quantity": 2, "status": "open"},
        1,
    ),
    expected={
        "status": "rejected",
        "accounts": {"gold": {1: 19, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 10,
            "quantity": 2,
            "status": "open",
        },
        "receipt": None,
        "reason": "not_enough_gold",
    },
    description="Покупка всего лота отклоняется при нехватке одной монеты",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"gold": {1: 19, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 10, "quantity": 2, "status": "closed"},
        1,
    ),
    expected={
        "status": "rejected",
        "accounts": {"gold": {1: 19, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 10,
            "quantity": 2,
            "status": "closed",
        },
        "receipt": None,
        "reason": "lot_closed",
    },
    description="Закрытый лот проверяется раньше денег покупателя",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 10, "quantity": 0, "status": "open"},
        1,
    ),
    expected={
        "status": "rejected",
        "accounts": {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 10,
            "quantity": 0,
            "status": "open",
        },
        "receipt": None,
        "reason": "lot_closed",
    },
    description="Нулевой остаток считается закрытым даже со статусом open",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 10, "quantity": 2, "status": "open"},
        1,
        0,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 80, 2: 20}, "bags": {1: {"ore": 2}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 10,
            "quantity": 0,
            "status": "closed",
        },
        "receipt": {"quantity": 2, "gross": 20, "fee": 0},
        "reason": None,
    },
    description="Нулевая комиссия оставляет всю выручку продавцу",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "L", "seller_id": 2, "item": "ore", "price": 10, "quantity": 2, "status": "open"},
        1,
        100,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 80, 2: 0}, "bags": {1: {"ore": 2}, 2: {}}, "treasury": 20},
        "lot": {
            "id": "L",
            "seller_id": 2,
            "item": "ore",
            "price": 10,
            "quantity": 0,
            "status": "closed",
        },
        "receipt": {"quantity": 2, "gross": 20, "fee": 20},
        "reason": None,
    },
    description="Комиссия сто процентов отправляет всю выручку в казну",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "gold": {1: 50, 2: 5, 3: 9},
            "bags": {1: {"ore": 4, "potion": 2}, 2: {"ore": 7}, 3: {}},
            "treasury": 8,
        },
        {"id": "R", "seller_id": 2, "item": "ore", "price": 7, "quantity": 3, "status": "open"},
        1,
        13,
    ),
    expected={
        "status": "bought",
        "accounts": {
            "gold": {1: 29, 2: 24, 3: 9},
            "bags": {1: {"ore": 7, "potion": 2}, 2: {"ore": 7}, 3: {}},
            "treasury": 10,
        },
        "lot": {
            "id": "R",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 0,
            "status": "closed",
        },
        "receipt": {"quantity": 3, "gross": 21, "fee": 2},
        "reason": None,
    },
    description="Дробная комиссия округляется вниз; соседние счета и предметы сохраняются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"gold": {1: 21, 2: 9}, "bags": {1: {"ore": 1}, 2: {}}, "treasury": 4},
        {"id": "R", "seller_id": 2, "item": "ore", "price": 7, "quantity": 3, "status": "open"},
        1,
        33,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 0, 2: 24}, "bags": {1: {"ore": 4}, 2: {}}, "treasury": 10},
        "lot": {
            "id": "R",
            "seller_id": 2,
            "item": "ore",
            "price": 7,
            "quantity": 0,
            "status": "closed",
        },
        "receipt": {"quantity": 3, "gross": 21, "fee": 6},
        "reason": None,
    },
    description="Ровно достаточный баланс расходуется до нуля",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"gold": {1: 1, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0},
        {"id": "tiny", "seller_id": 2, "item": "ore", "price": 1, "quantity": 1, "status": "open"},
        1,
    ),
    expected={
        "status": "bought",
        "accounts": {"gold": {1: 0, 2: 1}, "bags": {1: {"ore": 1}, 2: {}}, "treasury": 0},
        "lot": {
            "id": "tiny",
            "seller_id": 2,
            "item": "ore",
            "price": 1,
            "quantity": 0,
            "status": "closed",
        },
        "receipt": {"quantity": 1, "gross": 1, "fee": 0},
        "reason": None,
    },
    description="Маленькая сделка не округляет комиссию вверх",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "gold": {"b": 30, "s": 12},
            "bags": {"b": {"wood": 2, "stone": 2}, "s": {}},
            "treasury": 1,
        },
        {
            "id": "wood",
            "seller_id": "s",
            "item": "wood",
            "price": 6,
            "quantity": 4,
            "status": "open",
        },
        "b",
        25,
    ),
    expected={
        "status": "bought",
        "accounts": {
            "gold": {"b": 6, "s": 30},
            "bags": {"b": {"wood": 6, "stone": 2}, "s": {}},
            "treasury": 7,
        },
        "lot": {
            "id": "wood",
            "seller_id": "s",
            "item": "wood",
            "price": 6,
            "quantity": 0,
            "status": "closed",
        },
        "receipt": {"quantity": 4, "gross": 24, "fee": 6},
        "reason": None,
    },
    description="Строковые идентификаторы и уже накопленное золото сохраняются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_xla19_buy_lot(accounts, lot, buyer_id, fee_percent=10): ...
