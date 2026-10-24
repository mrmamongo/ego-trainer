def task_di12_total_by_category(entries):
    result = {}
    for amount, category in entries:
        if category not in result:
            result[category] = {"total": 0, "count": 0}
        result[category]["total"] = result[category]["total"] + amount
        result[category]["count"] = result[category]["count"] + 1
    return result
