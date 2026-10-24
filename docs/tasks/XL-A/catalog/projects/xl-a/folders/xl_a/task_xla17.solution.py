def given_craft(inventory, recipe):
    result = dict(inventory)
    required = dict(recipe["ingredients"])
    for item, qty in recipe.get("tools", {}).items():
        required[item] = required.get(item, 0) + qty
    missing = {
        item: required[item] - inventory.get(item, 0)
        for item in sorted(required)
        if inventory.get(item, 0) < required[item]
    }
    if missing:
        return {"status": "missing", "inventory": result, "missing": missing}
    for item, qty in recipe["ingredients"].items():
        result[item] = result.get(item, 0) - qty
    product = recipe["product"]
    result[product["item"]] = result.get(product["item"], 0) + product["qty"]
    return {"status": "crafted", "inventory": result, "missing": {}}


def task_xla17_craft_queue(inventory, orders, recipes):
    current = dict(inventory)
    reports = []
    crafted_count = 0
    for order in orders:
        recipe_id = order["recipe_id"]
        if recipe_id not in recipes:
            reports.append(
                {"id": order["id"], "status": "rejected", "reason": "unknown_recipe", "missing": {}}
            )
            continue
        crafted = given_craft(current, recipes[recipe_id])
        if crafted["status"] == "crafted":
            current = crafted["inventory"]
            crafted_count += 1
            reports.append({"id": order["id"], "status": "crafted", "reason": None, "missing": {}})
        else:
            reports.append(
                {
                    "id": order["id"],
                    "status": "rejected",
                    "reason": "missing_resources",
                    "missing": crafted["missing"],
                }
            )
    return {"inventory": current, "orders": reports, "crafted_count": crafted_count}
