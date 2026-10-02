from copy import deepcopy


def given_run_action(state, command):
    args = command.get("args", {})
    tool = command.get("tool")
    updated = {
        "events": {
            key: {
                "title": event["title"],
                "capacity": event["capacity"],
                "members": list(event["members"]),
            }
            for key, event in state["events"].items()
        },
        "announcements": [dict(item) for item in state["announcements"]],
        "next_id": state["next_id"],
    }
    result = None
    reason = None
    if tool == "create_event":
        title, capacity = args.get("title"), args.get("capacity")
        if not isinstance(title, str) or not title.strip():
            reason = "invalid_title"
        elif type(capacity) is not int or capacity < 1:
            reason = "invalid_capacity"
        else:
            event_id = "e" + str(updated["next_id"])
            updated["events"][event_id] = {
                "title": title.strip(),
                "capacity": capacity,
                "members": [],
            }
            updated["next_id"] += 1
            result = {"event_id": event_id}
    elif tool == "join_event":
        event_id, member_id = args.get("event_id"), args.get("member_id")
        if event_id not in updated["events"]:
            reason = "unknown_event"
        elif not isinstance(member_id, str) or not member_id:
            reason = "invalid_member"
        else:
            event = updated["events"][event_id]
            if member_id in event["members"]:
                reason = "already_joined"
            elif len(event["members"]) >= event["capacity"]:
                reason = "event_full"
            else:
                event["members"].append(member_id)
                result = {"event_id": event_id, "member_id": member_id}
    elif tool == "prepare_announcement":
        event_id, text = args.get("event_id"), args.get("text")
        if event_id not in updated["events"]:
            reason = "unknown_event"
        elif not isinstance(text, str) or not text.strip():
            reason = "invalid_text"
        else:
            index = len(updated["announcements"])
            updated["announcements"].append({"event_id": event_id, "text": text.strip()})
            result = {"announcement_index": index}
    else:
        reason = "unknown_tool"
    if reason is not None:
        return {"status": "rejected", "state": updated, "result": None, "reason": reason}
    return {"status": "done", "state": updated, "result": result, "reason": None}


def given_resolve_args(args, results):
    resolved = {}
    for key, value in args.items():
        if isinstance(value, dict) and "from_step" in value:
            step_id, field = value["from_step"], value["field"]
            if step_id not in results:
                return None, "dependency_failed:" + step_id
            if field not in results[step_id]:
                return None, "missing_result_field:" + step_id + ":" + field
            resolved[key] = results[step_id][field]
        else:
            resolved[key] = value
    return resolved, None


def task_xla26_run_plan(state, steps):
    updated = deepcopy(state)
    reports = []
    results = {}
    stopped = None
    for step in steps:
        step_id = step["id"]
        if stopped is not None:
            reports.append(
                {
                    "id": step_id,
                    "status": "skipped",
                    "result": None,
                    "reason": "stopped_after:" + stopped,
                }
            )
            continue
        args, error = given_resolve_args(step["args"], results)
        if error is not None:
            status, result, reason = "rejected", None, error
        else:
            action = given_run_action(updated, {"tool": step["tool"], "args": args})
            updated = action["state"]
            status, result, reason = action["status"], action["result"], action["reason"]
        reports.append({"id": step_id, "status": status, "result": result, "reason": reason})
        if status == "done":
            results[step_id] = result
        elif step["critical"]:
            stopped = step_id
    return {
        "state": updated,
        "steps": reports,
        "ok": all(report["status"] == "done" for report in reports),
    }
