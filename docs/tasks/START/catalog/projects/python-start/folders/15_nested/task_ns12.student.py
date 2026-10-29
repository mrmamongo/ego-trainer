# Сейчас функция считает только элементы верхнего уровня.
def task_ns12_count_leaves(data):
    if type(data) is dict:
        return len(data)
    if type(data) is list:
        return len(data)
    return 1
