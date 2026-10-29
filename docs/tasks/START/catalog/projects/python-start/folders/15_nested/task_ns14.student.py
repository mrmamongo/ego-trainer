def given_deep_copy(data):
    """GIVEN: полная копия вложенной структуры: ни одной общей коробки с исходной."""
    import json
    return json.loads(json.dumps(data))


# Сейчас сливается только верхний уровень, а вложенное берётся у пользователя целиком.
def task_ns14_merge_settings(defaults, user):
    result = given_deep_copy(defaults)
    for key in user:
        result[key] = user[key]
    return result
