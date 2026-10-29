def task_ns12_count_leaves(data):
    if type(data) is dict:
        total = 0
        for value in data.values():
            total = total + task_ns12_count_leaves(value)
        return total
    if type(data) is list:
        total = 0
        for item in data:
            total = total + task_ns12_count_leaves(item)
        return total
    return 1
