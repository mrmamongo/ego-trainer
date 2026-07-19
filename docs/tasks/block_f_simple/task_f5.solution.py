def task_f5_vip_in_order(order):
    for item in order.get("items", []):
        if item.get("category") == "vip":
            return True
    return False
