# Сейчас функция возвращает суммы по категориям: {категория: сумма}.
def task_di12_total_by_category(entries):
    totals = {}
    for amount, category in entries:
        totals[category] = totals.get(category, 0) + amount
    return totals
