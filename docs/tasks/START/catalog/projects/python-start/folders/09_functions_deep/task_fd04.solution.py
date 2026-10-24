def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items


def task_fd04_two_baskets(first, second):
    basket_1 = add_item(first)
    basket_2 = add_item(second)
    return basket_1, basket_2
