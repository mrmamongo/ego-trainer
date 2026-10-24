from copy import deepcopy


def _create_event(state, args):
    title, capacity = args.get("title"), args.get("capacity")
    if not isinstance(title, str) or not title.strip():
        return None, "invalid_title"
    if type(capacity) is not int or capacity < 1:
        return None, "invalid_capacity"
    event_id = "e" + str(state["next_id"])
    state["events"][event_id] = {
        "title": title.strip(),
        "capacity": capacity,
        "members": [],
    }
    state["next_id"] += 1
    return {"event_id": event_id}, None


def _join_event(state, args):
    event_id, member_id = args.get("event_id"), args.get("member_id")
    if event_id not in state["events"]:
        return None, "unknown_event"
    if not isinstance(member_id, str) or not member_id:
        return None, "invalid_member"
    event = state["events"][event_id]
    if member_id in event["members"]:
        return None, "already_joined"
    if len(event["members"]) >= event["capacity"]:
        return None, "event_full"
    event["members"].append(member_id)
    return {"event_id": event_id, "member_id": member_id}, None


def _prepare_announcement(state, args):
    event_id, text = args.get("event_id"), args.get("text")
    if event_id not in state["events"]:
        return None, "unknown_event"
    if not isinstance(text, str) or not text.strip():
        return None, "invalid_text"
    index = len(state["announcements"])
    state["announcements"].append({"event_id": event_id, "text": text.strip()})
    return {"announcement_index": index}, None


def task_xla25_run_action(state, command):
    updated = deepcopy(state)
    handlers = {
        "create_event": _create_event,
        "join_event": _join_event,
        "prepare_announcement": _prepare_announcement,
    }
    handler = handlers.get(command["tool"])
    if handler is None:
        result, reason = None, "unknown_tool"
    else:
        result, reason = handler(updated, command["args"])
    return {
        "status": "done" if reason is None else "rejected",
        "state": updated,
        "result": result,
        "reason": reason,
    }
