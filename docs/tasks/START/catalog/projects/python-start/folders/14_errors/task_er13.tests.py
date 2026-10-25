from ego.testing import case, rules

@case(
    args=({"gold": 100, "items": ["меч"]}, {"tool": "buy", "item": "щит", "price": 30}),
    expected={"status": "done", "state": {"gold": 70, "items": ["меч", "щит"]}, "result": {"item": "щит"}, "reason": None},
    description='покупка проходит',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"gold": 100, "items": ["меч"]}, {"tool": "buy", "item": "меч", "price": 30}),
    expected={"status": "rejected", "state": {"gold": 100, "items": ["меч"]}, "result": None, "reason": "already_owned"},
    description='предмет уже есть',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 10, "items": []}, {"tool": "buy", "item": "щит", "price": 30}),
    expected={"status": "rejected", "state": {"gold": 10, "items": []}, "result": None, "reason": "not_enough_gold"},
    description='не хватает золота',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 5, "items": ["меч", "щит"]}, {"tool": "drop", "item": "меч"}),
    expected={"status": "done", "state": {"gold": 5, "items": ["щит"]}, "result": {"item": "меч"}, "reason": None},
    description='выбросить предмет',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"gold": 5, "items": ["щит"]}, {"tool": "drop", "item": "меч"}),
    expected={"status": "rejected", "state": {"gold": 5, "items": ["щит"]}, "result": None, "reason": "not_owned"},
    description='выбрасываем то, чего нет',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 50, "items": []}, {"tool": "buy", "item": "щит", "price": 0}),
    expected={"status": "rejected", "state": {"gold": 50, "items": []}, "result": None, "reason": "bad_price"},
    description='нулевая цена',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 50, "items": []}, {"tool": "buy", "item": "щит", "price": "30"}),
    expected={"status": "rejected", "state": {"gold": 50, "items": []}, "result": None, "reason": "bad_price"},
    description='цена — строка',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 0, "items": ["меч"]}, {"tool": "buy", "item": "меч", "price": 10}),
    expected={"status": "rejected", "state": {"gold": 0, "items": ["меч"]}, "result": None, "reason": "already_owned"},
    description='already_owned важнее not_enough_gold',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    hide_expected=True,
)

@case(
    args=({"gold": 0, "items": []}, {"tool": "buy", "item": "меч", "price": -1}),
    expected={"status": "rejected", "state": {"gold": 0, "items": []}, "result": None, "reason": "bad_price"},
    description='bad_price важнее not_enough_gold',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    hide_expected=True,
)

@case(
    args=({"gold": 10, "items": ["меч"]}, {"tool": "sell", "item": "меч"}),
    expected={"status": "rejected", "state": {"gold": 10, "items": ["меч"]}, "result": None, "reason": "unknown_tool"},
    description='неизвестное действие',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 30, "items": []}, {"tool": "buy", "item": "щит", "price": 30}),
    expected={"status": "done", "state": {"gold": 0, "items": ["щит"]}, "result": {"item": "щит"}, "reason": None},
    description='граница: тратим всё золото',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)


@rules(require_functions=["given_rejected"])

def task_er13_apply_action(state, action):
    ...
