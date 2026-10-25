def given_rejected(state, reason):
    """GIVEN: ответ-отказ: исходное состояние, result=None, reason=код."""
    return {"status": "rejected", "state": state, "result": None, "reason": reason}


def task_er13_apply_action(state, action):
    # buy: bad_price, already_owned, not_enough_gold; drop: not_owned; иначе unknown_tool.
    return given_rejected(state, "unknown_tool")
