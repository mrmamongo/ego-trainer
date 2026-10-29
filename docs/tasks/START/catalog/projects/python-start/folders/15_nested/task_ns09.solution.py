def given_deep_copy(data):
    """GIVEN: полная копия вложенной структуры: ни одной общей коробки с исходной."""
    import json
    return json.loads(json.dumps(data))


def task_ns09_delete_path(data, path):
    result = given_deep_copy(data)
    key = path[0]
    if key not in result:
        return result
    if len(path) == 1:
        del result[key]
        return result
    child = result[key]
    if type(child) is not dict:
        return result
    new_child = task_ns09_delete_path(child, path[1:])
    if new_child == {} and child != {}:
        del result[key]
    else:
        result[key] = new_child
    return result
