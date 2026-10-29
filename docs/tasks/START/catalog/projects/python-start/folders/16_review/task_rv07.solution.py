def task_rv07_discount(total, is_new=False):
    if is_new and total >= 500:
        return 20
    if total >= 5000:
        return 15
    if total >= 1000:
        return 5
    return 0
