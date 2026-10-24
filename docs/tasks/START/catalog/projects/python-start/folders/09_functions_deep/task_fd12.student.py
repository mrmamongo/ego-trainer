# Сейчас функция работает по старому правилу: слишком дорогие цены пропускаются.
def task_fd12_take_within_budget(items, budget):
    result = []
    spent = 0
    for item in items:
        if spent + item > budget:
            continue
        result.append(item)
        spent = spent + item
    return result
