# Сейчас функция работает по старым правилам: скидка зависит только от суммы.
def task_rv07_discount(total):
    if total >= 5000:
        return 15
    if total >= 1000:
        return 5
    return 0
