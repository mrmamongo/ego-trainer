def task_bk20_take_skip_too_big(prices, budget):
    total = 0
    result = []
    for price in prices:
        if total + price > budget:
            continue
        total = total + price
        result.append(price)
    return result
