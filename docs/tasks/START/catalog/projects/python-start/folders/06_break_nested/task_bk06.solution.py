def task_bk06_sum_positive(numbers):
    total = 0
    for number in numbers:
        if number <= 0:
            continue
        total = total + number
    return total
