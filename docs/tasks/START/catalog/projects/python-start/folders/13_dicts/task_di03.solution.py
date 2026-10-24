def task_di03_total_stock(stock, items):
    total = 0
    for item in items:
        total = total + stock.get(item, 0)
    return total
