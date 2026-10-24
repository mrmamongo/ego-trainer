def task_bk04_sum_skip_negative(numbers):
    total = 0
    for number in numbers:
        if number < 0:
            continue
        total = total + number
    return total
