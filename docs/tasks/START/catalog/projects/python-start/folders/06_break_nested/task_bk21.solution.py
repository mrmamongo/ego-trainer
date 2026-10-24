def task_bk21_take_newest_skip_too_big(prices, budget):
    total = 0
    result = []
    for price in reversed(prices):
        if total + price > budget:
            continue
        total = total + price
        result.append(price)
    result.reverse()
    return result
