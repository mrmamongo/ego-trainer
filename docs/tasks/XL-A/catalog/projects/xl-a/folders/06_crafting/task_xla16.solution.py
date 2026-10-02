def task_xla16_craft(inventory, recipe):
    result = dict(inventory)
    required = dict(recipe["ingredients"])
    for item, quantity in recipe.get("tools", {}).items():
        required[item] = required.get(item, 0) + quantity
    missing = {
        item: required[item] - inventory.get(item, 0)
        for item in sorted(required)
        if inventory.get(item, 0) < required[item]
    }
    if missing:
        return {"status": "missing", "inventory": result, "missing": missing}
    for item, quantity in recipe["ingredients"].items():
        result[item] = result.get(item, 0) - quantity
    product = recipe["product"]
    result[product["item"]] = result.get(product["item"], 0) + product["qty"]
    return {"status": "crafted", "inventory": result, "missing": {}}
