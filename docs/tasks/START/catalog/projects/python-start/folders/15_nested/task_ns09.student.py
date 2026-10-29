def given_deep_copy(data):
    """GIVEN: полная копия вложенной структуры: ни одной общей коробки с исходной."""
    import json
    return json.loads(json.dumps(data))


# Сейчас функция удаляет ключ верхнего уровня прямо во входе.
def task_ns09_delete_path(data, path):
    del data[path[0]]
    return data
