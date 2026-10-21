def task_l21_average(numbers):
    total = 0
    count = 0
    for number in numbers:
        total = total + number
        count = count + 1
    if count == 0:
        return 0.0
    return total / count
