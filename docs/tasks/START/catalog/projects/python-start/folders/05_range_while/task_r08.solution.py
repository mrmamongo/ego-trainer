def task_r08_sum_even(a, b):
    total = 0
    for i in range(a, b + 1):
        if i % 2 == 0:
            total = total + i
    return total
