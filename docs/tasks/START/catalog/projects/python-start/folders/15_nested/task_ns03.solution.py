def task_ns03_nested_sum(items):
    total = 0
    for item in items:
        if type(item) is list:
            total = total + task_ns03_nested_sum(item)
        elif type(item) is int:
            total = total + item
    return total
