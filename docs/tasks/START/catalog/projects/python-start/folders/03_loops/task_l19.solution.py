def task_l19_max_value(numbers):
    best = numbers[0]
    for number in numbers:
        if number > best:
            best = number
    return best
