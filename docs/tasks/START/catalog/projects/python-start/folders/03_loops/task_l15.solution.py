def task_l15_has_negative(numbers):
    found = False
    for number in numbers:
        if number < 0:
            found = True
    return found
