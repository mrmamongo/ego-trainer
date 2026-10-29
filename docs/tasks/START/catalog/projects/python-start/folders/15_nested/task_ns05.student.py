def task_ns05_depth(items):
    deepest = 0
    for item in items:
        if type(item) is list:
            pass  # здесь нужна глубина вложенного списка item
    return deepest + 1
