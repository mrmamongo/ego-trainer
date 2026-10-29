def given_deep_copy(data):
    """GIVEN: полная копия вложенной структуры: ни одной общей коробки с исходной."""
    import json
    return json.loads(json.dumps(data))


def task_ns11_set_path(data, path, value):
    result = given_deep_copy(data)
    current = result
    walked = []
    for key in path[:-1]:
        walked.append(key)
        if key not in current:
            current[key] = {}
        elif type(current[key]) is not dict:
            return {
                "status": "rejected",
                "data": given_deep_copy(data),
                "reason": "not_a_dict",
                "at": ".".join(walked),
            }
        current = current[key]
    current[path[-1]] = value
    return {"status": "done", "data": result, "reason": None, "at": None}
