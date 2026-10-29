def given_deep_copy(data):
    """GIVEN: полная копия вложенной структуры: ни одной общей коробки с исходной."""
    import json
    return json.loads(json.dumps(data))


# Сейчас функция пишет прямо во вход и понимает только путь из одного ключа.
def task_ns08_set_path(data, path, value):
    data[path[0]] = value
    return data
