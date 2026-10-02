from copy import deepcopy


def _path_conflicts(profile, path):
    current = profile
    for key in path[:-1]:
        if key not in current:
            return False
        current = current[key]
        if not isinstance(current, dict):
            return True
    return path[-1] in current and isinstance(current[path[-1]], dict)


def task_xla22_update_profile(profile, updates):
    updated = deepcopy(profile)
    changes = []
    errors = []
    for index, update in enumerate(updates):
        path = update["path"]
        value = update["value"]
        if _path_conflicts(updated, path):
            errors.append({"index": index, "path": list(path), "reason": "path_conflict"})
            continue
        current = updated
        for key in path[:-1]:
            current = current.setdefault(key, {})
        key = path[-1]
        present = key in current
        before = current.get(key)
        if present and type(before) is type(value) and before == value:
            continue
        current[key] = value
        changes.append(
            {
                "path": list(path),
                "kind": "changed" if present else "added",
                "before": before,
                "after": value,
            }
        )
    return {"profile": updated, "changes": changes, "errors": errors}
