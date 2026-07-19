def task_d4_inventory_value(inventory):
    result = {}
    for item in inventory:
        rar = item["rarity"]
        value = item["qty"] * item["unit_price"]
        result[rar] = result.get(rar, 0) + value
    return result
