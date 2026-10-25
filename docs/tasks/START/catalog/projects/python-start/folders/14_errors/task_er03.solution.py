def task_er03_safe_int(text, default):
    try:
        return int(text)
    except ValueError:
        return default
