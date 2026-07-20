def task_h1_inventory_stack(items):
    result = {}
    for item in items:
        n = item["name"]
        result[n] = result.get(n, 0) + item["qty"]
    return result
