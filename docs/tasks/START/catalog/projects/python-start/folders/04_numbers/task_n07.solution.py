def task_n07_average(numbers):
    total = 0
    for number in numbers:
        total = total + number
    if len(numbers) == 0:
        return 0.0
    return total / len(numbers)
