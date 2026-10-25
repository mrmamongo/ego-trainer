def given_apply(state, command):
    """GIVEN: применить команду к складу; вернуть {ok, state, value, error}.

    Порядок проверок: unknown_tool, bad_qty, потом (для take) unknown_item, not_enough.
    При отказе state — исходное состояние без изменений.
    """
    tool = command["tool"]
    item = command["item"]
    qty = command["qty"]
    if tool not in ("put", "take"):
        return {"ok": False, "state": state, "value": None, "error": "unknown_tool"}
    if qty <= 0:
        return {"ok": False, "state": state, "value": None, "error": "bad_qty"}
    stock = dict(state["stock"])
    if tool == "put":
        stock[item] = stock.get(item, 0) + qty
    else:
        if item not in stock:
            return {"ok": False, "state": state, "value": None, "error": "unknown_item"}
        if stock[item] < qty:
            return {"ok": False, "state": state, "value": None, "error": "not_enough"}
        stock[item] = stock[item] - qty
    return {"ok": True, "state": {"stock": stock}, "value": {"item": item, "qty": qty}, "error": None}


def task_er14_run(state, command):
    handled = given_apply(state, command)
    if handled["ok"]:
        return {
            "status": "done",
            "state": handled["state"],
            "result": handled["value"],
            "reason": None,
        }
    return {
        "status": "rejected",
        "state": state,
        "result": None,
        "reason": handled["error"],
    }
