def task_bk19_take_while_fits(prices, budget):
    total = 0
    result = []
    for price in prices:
        if total + price > budget:
            break
        total = total + price
        result.append(price)
    return result
