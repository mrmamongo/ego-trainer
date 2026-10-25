from ego.testing import case, rules

# --- обычный режим: старое поведение, плюс preview_state = None ---

@case(
    args=({"gold": 100, "items": ["меч"]}, {"tool": "buy", "item": "щит", "price": 30}),
    expected={"status": "done", "state": {"gold": 70, "items": ["меч", "щит"]}, "result": {"item": "щит"}, "reason": None, "preview_state": None},
    description='старое: покупка применяется',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"gold": 10, "items": []}, {"tool": "buy", "item": "щит", "price": 30}),
    expected={"status": "rejected", "state": {"gold": 10, "items": []}, "result": None, "reason": "not_enough_gold", "preview_state": None},
    description='старое: отказ',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 5, "items": ["меч", "щит"]}, {"tool": "drop", "item": "меч"}),
    expected={"status": "done", "state": {"gold": 5, "items": ["щит"]}, "result": {"item": "меч"}, "reason": None, "preview_state": None},
    description='старое: drop применяется',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"gold": 5, "items": []}, {"tool": "sell", "item": "меч"}),
    expected={"status": "rejected", "state": {"gold": 5, "items": []}, "result": None, "reason": "unknown_tool", "preview_state": None},
    description='старое: неизвестное действие',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

# --- новый режим preview ---

@case(
    args=({"gold": 100, "items": []}, {"tool": "buy", "item": "щит", "price": 30}, True),
    expected={"status": "preview", "state": {"gold": 100, "items": []}, "result": {"item": "щит"}, "reason": None, "preview_state": {"gold": 70, "items": ["щит"]}},
    description='preview покупки: состояние не меняется, прогноз в preview_state',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 10, "items": []}, {"tool": "buy", "item": "щит", "price": 30}, True),
    expected={"status": "rejected", "state": {"gold": 10, "items": []}, "result": None, "reason": "not_enough_gold", "preview_state": None},
    description='preview отказа выглядит как обычный отказ',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 5, "items": ["меч"]}, {"tool": "drop", "item": "меч"}, True),
    expected={"status": "preview", "state": {"gold": 5, "items": ["меч"]}, "result": {"item": "меч"}, "reason": None, "preview_state": {"gold": 5, "items": []}},
    description='preview drop',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"gold": 5, "items": ["меч"]}, {"tool": "drop", "item": "меч"}, False),
    expected={"status": "done", "state": {"gold": 5, "items": []}, "result": {"item": "меч"}, "reason": None, "preview_state": None},
    description='preview=False — обычный режим',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"gold": 30, "items": []}, {"tool": "buy", "item": "щит", "price": 0}, True),
    expected={"status": "rejected", "state": {"gold": 30, "items": []}, "result": None, "reason": "bad_price", "preview_state": None},
    description='preview с неверной ценой',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    hide_expected=True,
)


@rules(require_functions=["given_rejected"])

def task_er15_apply_action(state, action, preview=False):
    ...
