from ego.testing import case, rules

@case(
    args=(100, 30),
    expected={"status": "done", "balance": 70},
    description='хватает денег',
    level="smoke",
    comparison="value",
)

@case(
    args=(100, 130),
    expected={"status": "rejected", "reason": "budget"},
    description='не хватает денег',
    level="smoke",
    comparison="value",
)

@case(
    args=(100, 0),
    expected={"status": "rejected", "reason": "bad_amount"},
    description='нулевая сумма',
    level="smoke",
    comparison="value",
)

@case(
    args=(100, 100),
    expected={"status": "done", "balance": 0},
    description='граница: тратим всё',
    level="full",
    comparison="value",
)

@case(
    args=(100, 101),
    expected={"status": "rejected", "reason": "budget"},
    description='граница: на рубль больше',
    level="full",
    comparison="value",
)

@case(
    args=(50, -5),
    expected={"status": "rejected", "reason": "bad_amount"},
    description='отрицательная сумма',
    level="full",
    comparison="value",
)

@case(
    args=(0, 1),
    expected={"status": "rejected", "reason": "budget"},
    description='баланс ноль',
    level="full",
    comparison="value",
)

@case(
    args=(0, 0),
    expected={"status": "rejected", "reason": "bad_amount"},
    description='ноль и ноль: сначала проверяется сумма',
    level="full",
    comparison="value",
    hide_expected=True,
)


@rules(require_functions=["spend"])

def task_er10_pay(balance, amount):
    ...
