def task_rv10_get_path(data, path, default=None):
    current = data
    for key in path.split("."):
        try:
            current = current[key]
        except (KeyError, TypeError):
            return default
    return current
