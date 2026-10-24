def task_di17_merge_inventories(a, b):
    result = dict(a)
    for item, qty in b.items():
        result[item] = result.get(item, 0) + qty
    return result
