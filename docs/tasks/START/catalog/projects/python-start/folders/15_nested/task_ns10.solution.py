def task_ns10_deep_copy(data):
    if type(data) is dict:
        result = {}
        for key, value in data.items():
            result[key] = task_ns10_deep_copy(value)
        return result
    if type(data) is list:
        result = []
        for item in data:
            result.append(task_ns10_deep_copy(item))
        return result
    return data
