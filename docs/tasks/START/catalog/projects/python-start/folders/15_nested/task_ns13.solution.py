def given_deep_copy(data):
    """GIVEN: полная копия вложенной структуры: ни одной общей коробки с исходной."""
    import json
    return json.loads(json.dumps(data))


def task_ns13_delete_path(data, path):
    result = given_deep_copy(data)
    key = path[0]
    if key not in result:
        return {"data": result, "removed": []}
    if len(path) == 1:
        del result[key]
        return {"data": result, "removed": [key]}
    child = result[key]
    if type(child) is not dict:
        return {"data": result, "removed": []}
    inner = task_ns13_delete_path(child, path[1:])
    if inner["removed"] == []:
        return {"data": result, "removed": []}
    removed = []
    for name in inner["removed"]:
        removed.append(key + "." + name)
    if inner["data"] == {}:
        del result[key]
        removed.append(key)
    else:
        result[key] = inner["data"]
    return {"data": result, "removed": removed}
