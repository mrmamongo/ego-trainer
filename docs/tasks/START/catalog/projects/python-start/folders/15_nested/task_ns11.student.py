def given_deep_copy(data):
    """GIVEN: полная копия вложенной структуры: ни одной общей коробки с исходной."""
    import json
    return json.loads(json.dumps(data))


# Сейчас функция возвращает просто новую структуру.
# Число или строка на пути молча заменяются словарём.
def task_ns11_set_path(data, path, value):
    result = given_deep_copy(data)
    current = result
    for key in path[:-1]:
        if key not in current or type(current[key]) is not dict:
            current[key] = {}
        current = current[key]
    current[path[-1]] = value
    return result
