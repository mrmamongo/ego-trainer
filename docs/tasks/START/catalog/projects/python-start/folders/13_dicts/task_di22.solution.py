def task_di22_top_categories(totals, n):
    pairs = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
    result = []
    for category, total in pairs[:n]:
        result.append([category, total])
    return result
