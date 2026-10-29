def task_ns07_get_path(data, path, default):
    current = data
    for key in path:
        if type(current) is not dict or key not in current:
            return default
        current = current[key]
    return current
