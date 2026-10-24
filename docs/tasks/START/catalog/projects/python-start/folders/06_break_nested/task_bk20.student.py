def task_bk20_take_skip_too_big(prices, budget):
    # Ниже решение прошлой задачи (BK19): оно останавливается на первой цене, что не влезла.
    # Измени его так, чтобы такая цена пропускалась, а обход продолжался дальше.
    total = 0
    result = []
    for price in prices:
        if total + price > budget:
            break
        total = total + price
        result.append(price)
    return result
