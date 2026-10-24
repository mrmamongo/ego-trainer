def task_bk05_sum_until_zero(numbers):
    total = 0
    for number in numbers:
        if number == 0:
            break
        total = total + number
    return total
