def given_deep_copy(data):
    """GIVEN: полная копия вложенной структуры: ни одной общей коробки с исходной."""
    import json
    return json.loads(json.dumps(data))


def task_ns14_merge_settings(defaults, user):
    result = given_deep_copy(defaults)
    for key, value in user.items():
        if key in result and type(result[key]) is dict and type(value) is dict:
            result[key] = task_ns14_merge_settings(result[key], value)
        else:
            result[key] = given_deep_copy(value)
    return result
