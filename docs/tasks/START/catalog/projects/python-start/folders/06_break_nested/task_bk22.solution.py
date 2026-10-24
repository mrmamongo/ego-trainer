def task_bk22_take_with_required_first(prices, budget):
    if len(prices) == 0:
        return []
    if prices[0] > budget:
        return []
    total = prices[0]
    result = []
    for index in range(len(prices) - 1, 0, -1):
        price = prices[index]
        if total + price > budget:
            continue
        total = total + price
        result.append(price)
    result.append(prices[0])
    result.reverse()
    return result
