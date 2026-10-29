def task_ns04_flatten(items):
    result = []
    for item in items:
        if type(item) is list:
            result = result + task_ns04_flatten(item)
        else:
            result.append(item)
    return result
