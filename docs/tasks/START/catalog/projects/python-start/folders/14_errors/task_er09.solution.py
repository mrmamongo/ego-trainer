PRICES = {"чай": 50, "кофе": 120, "булка": 70}


# Порядок проверок: no_items, duplicate_item, bad_qty, unknown_item, over_budget.
def task_er09_validate_order(order):
    items = order["items"]
    if len(items) == 0:
        return "no_items"
    seen = []
    for item in items:
        if item["name"] in seen:
            return "duplicate_item"
        seen.append(item["name"])
    for item in items:
        if type(item["qty"]) is not int or item["qty"] < 1:
            return "bad_qty"
    for item in items:
        if item["name"] not in PRICES:
            return "unknown_item"
    total = 0
    for item in items:
        total = total + PRICES[item["name"]] * item["qty"]
    if total > order["budget"]:
        return "over_budget"
    return "ok"
