def given_find_matches(items, field, value):
    """GIVEN: найти все записи с точным совпадением значения поля."""
    return [item for item in items if item[field] == value]


def task_xla13_prepare_action(raw, members, events):
    tool = raw["tool"]
    args = raw["args"]
    errors = []
    if tool == "create_event":
        title = args.get("title")
        title = title.strip() if isinstance(title, str) else ""
        capacity = args.get("capacity")
        if not title:
            errors.append("title_empty")
        if type(capacity) is not int or capacity < 1:
            errors.append("invalid_capacity")
        prepared = {"title": title, "capacity": capacity}
    elif tool == "join_event":
        member_name = args.get("member_name")
        member_name = member_name.strip() if isinstance(member_name, str) else ""
        event_title = args.get("event_title")
        event_title = event_title.strip() if isinstance(event_title, str) else ""
        member_matches = []
        event_matches = []
        if not member_name:
            errors.append("member_name_empty")
        else:
            member_matches = given_find_matches(members, "name", member_name)
            if not member_matches:
                errors.append("unknown_member")
            elif len(member_matches) > 1:
                errors.append("ambiguous_member")
        if not event_title:
            errors.append("event_title_empty")
        else:
            event_matches = given_find_matches(events, "title", event_title)
            if not event_matches:
                errors.append("unknown_event")
            elif len(event_matches) > 1:
                errors.append("ambiguous_event")
        if errors:
            return {"status": "rejected", "command": None, "errors": errors}
        member = member_matches[0]
        event = event_matches[0]
        if member["id"] in event["members"]:
            errors.append("already_joined")
        elif len(event["members"]) >= event["capacity"]:
            errors.append("event_full")
        prepared = {"member_id": member["id"], "event_id": event["id"]}
    else:
        return {"status": "rejected", "command": None, "errors": ["unknown_tool"]}
    if errors:
        return {"status": "rejected", "command": None, "errors": errors}
    return {"status": "ready", "command": {"tool": tool, "args": prepared}, "errors": []}
