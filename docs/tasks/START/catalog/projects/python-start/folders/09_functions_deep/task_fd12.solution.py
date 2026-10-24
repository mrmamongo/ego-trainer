def task_fd12_take_within_budget(items, budget):
    if len(items) > 0 and items[0] > budget:
        return []
    result = []
    spent = 0
    for item in items:
        if spent + item > budget:
            continue
        result.append(item)
        spent = spent + item
    return result
