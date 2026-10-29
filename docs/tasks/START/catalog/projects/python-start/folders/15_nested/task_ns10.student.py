# Сейчас копируется только верхний уровень, вложенное остаётся общим.
def task_ns10_deep_copy(data):
    if type(data) is dict:
        return dict(data)
    if type(data) is list:
        return list(data)
    return data
