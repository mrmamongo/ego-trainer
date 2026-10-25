PRICES = {"чай": 50, "кофе": 120, "булка": 70}


def task_er08_validate_order(order):
    items = order["items"]
    if len(items) == 0:
        return "no_items"
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
