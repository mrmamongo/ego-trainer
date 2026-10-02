def given_create_event(state, args):
    """GIVEN: чисто создать событие и вернуть {ok,state,value,error}."""
    import copy

    new_state = copy.deepcopy(state)
    event_id = f"e{new_state['next_id']}"
    new_state["next_id"] += 1
    new_state["events"].append(
        {"id": event_id, "title": args["title"], "capacity": args["capacity"], "members": []}
    )
    return {"ok": True, "state": new_state, "value": {"event_id": event_id}, "error": None}


def given_join_event(state, args):
    """GIVEN: чисто вступить в событие с фиксированным порядком отказов."""
    import copy

    new_state = copy.deepcopy(state)
    event = next((item for item in new_state["events"] if item["id"] == args["event_id"]), None)
    if event is None:
        return {"ok": False, "state": copy.deepcopy(state), "value": None, "error": "unknown_event"}
    if args["member_id"] in event["members"]:
        return {
            "ok": False,
            "state": copy.deepcopy(state),
            "value": None,
            "error": "already_joined",
        }
    if len(event["members"]) >= event["capacity"]:
        return {"ok": False, "state": copy.deepcopy(state), "value": None, "error": "event_full"}
    event["members"].append(args["member_id"])
    return {
        "ok": True,
        "state": new_state,
        "value": {"event_id": event["id"], "member_id": args["member_id"]},
        "error": None,
    }


def given_dispatch(state, command):
    """GIVEN: корректная обычная отправка; независима от XL-A14."""
    import copy

    if command["tool"] == "create_event":
        handled = given_create_event(state, command["args"])
    elif command["tool"] == "join_event":
        handled = given_join_event(state, command["args"])
    else:
        return {
            "status": "rejected",
            "state": copy.deepcopy(state),
            "result": None,
            "reason": "unknown_tool",
        }
    if not handled["ok"]:
        return {
            "status": "rejected",
            "state": copy.deepcopy(state),
            "result": None,
            "reason": handled["error"],
        }
    return {"status": "done", "state": handled["state"], "result": handled["value"], "reason": None}


def task_xla15_preview_action(state, command, mode="apply"):
    dispatched = given_dispatch(state, command)
    if mode == "apply":
        return {**dispatched, "preview_state": None}
    if dispatched["status"] == "rejected":
        return {**dispatched, "preview_state": None}
    return {
        "status": "preview",
        "state": state,
        "result": dispatched["result"],
        "reason": None,
        "preview_state": dispatched["state"],
    }
