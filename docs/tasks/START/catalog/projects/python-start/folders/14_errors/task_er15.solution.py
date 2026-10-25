def given_rejected(state, reason):
    """GIVEN: ответ-отказ: исходное состояние, result=None, reason=код."""
    return {"status": "rejected", "state": state, "result": None, "reason": reason}


def apply_now(state, action):
    tool = action["tool"]
    if tool == "buy":
        item = action["item"]
        price = action["price"]
        if type(price) is not int or price <= 0:
            return given_rejected(state, "bad_price")
        if item in state["items"]:
            return given_rejected(state, "already_owned")
        if price > state["gold"]:
            return given_rejected(state, "not_enough_gold")
        new_state = {"gold": state["gold"] - price, "items": state["items"] + [item]}
        return {"status": "done", "state": new_state, "result": {"item": item}, "reason": None}
    if tool == "drop":
        item = action["item"]
        if item not in state["items"]:
            return given_rejected(state, "not_owned")
        new_items = []
        for owned in state["items"]:
            if owned != item:
                new_items.append(owned)
        new_state = {"gold": state["gold"], "items": new_items}
        return {"status": "done", "state": new_state, "result": {"item": item}, "reason": None}
    return given_rejected(state, "unknown_tool")


def task_er15_apply_action(state, action, preview=False):
    answer = apply_now(state, action)
    if preview and answer["status"] == "done":
        return {
            "status": "preview",
            "state": state,
            "result": answer["result"],
            "reason": None,
            "preview_state": answer["state"],
        }
    answer["preview_state"] = None
    return answer
