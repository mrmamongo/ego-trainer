def task_ns05_depth(items):
    deepest = 0
    for item in items:
        if type(item) is list:
            inner = task_ns05_depth(item)
            if inner > deepest:
                deepest = inner
    return deepest + 1
