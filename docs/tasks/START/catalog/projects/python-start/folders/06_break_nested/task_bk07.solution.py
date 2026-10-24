def task_bk07_first_multiple(a, b, k):
    for number in range(a, b + 1):
        if number % k == 0:
            return number
    return -1
