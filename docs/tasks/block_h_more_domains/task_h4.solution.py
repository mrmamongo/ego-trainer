def task_h4_backpack(items, capacity):
    taken = []
    total_w = 0
    total_v = 0
    for item in items:
        if total_w + item["weight"] <= capacity:
            taken.append(item)
            total_w += item["weight"]
            total_v += item["value"]
    return {
        "taken": taken,
        "total_weight": total_w,
        "total_value": total_v,
        "remaining_capacity": capacity - total_w,
    }
