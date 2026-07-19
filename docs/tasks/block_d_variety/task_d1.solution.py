def task_d1_orders_by_category(orders):
    result = {}
    for o in orders:
        cat = o["category"]
        result[cat] = result.get(cat, 0) + o["amount"]
    return result
