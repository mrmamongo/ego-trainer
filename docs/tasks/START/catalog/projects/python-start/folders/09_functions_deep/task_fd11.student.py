# Сейчас функция работает по старому правилу: останавливается на первой цене, которая не влезла.
def task_fd11_take_within_budget(items, budget):
    result = []
    spent = 0
    for item in items:
        if spent + item > budget:
            break
        result.append(item)
        spent = spent + item
    return result
