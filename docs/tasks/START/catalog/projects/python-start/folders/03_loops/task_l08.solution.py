def task_l08_count_positive(numbers):
    count = 0
    for number in numbers:
        if number > 0:
            count = count + 1
    return count
