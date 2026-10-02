def task_xla18_craft_atomic(inventory, recipe):
    result = dict(inventory)
    for item in sorted(recipe["ingredients"]):
        if inventory.get(item, 0) < recipe["ingredients"][item]:
            return {"status": "rejected", "inventory": result, "missing_item": item}
    for item, quantity in recipe["ingredients"].items():
        result[item] = result.get(item, 0) - quantity
    product = recipe["product"]
    result[product["item"]] = result.get(product["item"], 0) + product["qty"]
    return {"status": "crafted", "inventory": result, "missing_item": None}
