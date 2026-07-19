def task_f3_count_pending(tasks):
    count = 0
    for t in tasks:
        if t["status"] == "pending":
            count += 1
    return count
