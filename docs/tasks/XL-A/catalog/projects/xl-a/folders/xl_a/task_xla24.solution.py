from copy import deepcopy


def _leaf_paths(value, path):
    if not isinstance(value, dict):
        return [list(path)]
    result = []
    for key in sorted(value):
        result.extend(_leaf_paths(value[key], [*path, key]))
    return result


def task_xla24_forget_topic(profile, path):
    updated = deepcopy(profile)
    if not path:
        return {"profile": {}, "removed_paths": _leaf_paths(updated, [])}

    current = updated
    ancestors = []
    for key in path[:-1]:
        if key not in current or not isinstance(current[key], dict):
            return {"profile": updated, "removed_paths": []}
        ancestors.append((current, key))
        current = current[key]
    key = path[-1]
    if key not in current:
        return {"profile": updated, "removed_paths": []}
    removed = _leaf_paths(current[key], list(path))
    del current[key]
    for parent, ancestor_key in reversed(ancestors):
        if parent[ancestor_key]:
            break
        del parent[ancestor_key]
    return {"profile": updated, "removed_paths": removed}
