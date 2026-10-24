def task_di16_inventory_add(inventory, item, qty):
    result = dict(inventory)
    result[item] = result.get(item, 0) + qty
    return result
