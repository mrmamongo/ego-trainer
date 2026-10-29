def task_ns07_get_path(data, path, default):
    current = data
    for key in path:
        current = current[key]
    return current
