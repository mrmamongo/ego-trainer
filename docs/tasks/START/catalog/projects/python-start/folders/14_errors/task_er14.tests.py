from ego.testing import case, rules

@case(
    args=({"stock": {"яблоки": 3}}, {"tool": "take", "item": "яблоки", "qty": 5}),
    expected={"status": "rejected", "state": {"stock": {"яблоки": 3}}, "result": None, "reason": "not_enough"},
    description='взять больше, чем есть',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"stock": {"яблоки": 3}}, {"tool": "take", "item": "яблоки", "qty": 2}),
    expected={"status": "done", "state": {"stock": {"яблоки": 1}}, "result": {"item": "яблоки", "qty": 2}, "reason": None},
    description='взять часть: успех',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"stock": {}}, {"tool": "put", "item": "груши", "qty": 4}),
    expected={"status": "done", "state": {"stock": {"груши": 4}}, "result": {"item": "груши", "qty": 4}, "reason": None},
    description='положить новый товар',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"stock": {"яблоки": 3}}, {"tool": "take", "item": "киви", "qty": 1}),
    expected={"status": "rejected", "state": {"stock": {"яблоки": 3}}, "result": None, "reason": "unknown_item"},
    description='такого товара нет',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"stock": {"яблоки": 3}}, {"tool": "put", "item": "яблоки", "qty": 0}),
    expected={"status": "rejected", "state": {"stock": {"яблоки": 3}}, "result": None, "reason": "bad_qty"},
    description='нулевое количество',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"stock": {"яблоки": 3}}, {"tool": "throw", "item": "яблоки", "qty": 1}),
    expected={"status": "rejected", "state": {"stock": {"яблоки": 3}}, "result": None, "reason": "unknown_tool"},
    description='неизвестное действие',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"stock": {"яблоки": 3}}, {"tool": "take", "item": "яблоки", "qty": 3}),
    expected={"status": "done", "state": {"stock": {"яблоки": 0}}, "result": {"item": "яблоки", "qty": 3}, "reason": None},
    description='граница: берём всё',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({"stock": {"яблоки": 3}}, {"tool": "put", "item": "яблоки", "qty": 2}),
    expected={"status": "done", "state": {"stock": {"яблоки": 5}}, "result": {"item": "яблоки", "qty": 2}, "reason": None},
    description='добавить к существующему',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)


@rules(require_functions=["given_apply"])

def task_er14_run(state, command):
    ...
