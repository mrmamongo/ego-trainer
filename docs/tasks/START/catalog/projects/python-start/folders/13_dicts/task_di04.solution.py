def task_di04_rename_key(d, old, new):
    result = {}
    for key, value in d.items():
        if key == old:
            result[new] = value
        else:
            result[key] = value
    return result
