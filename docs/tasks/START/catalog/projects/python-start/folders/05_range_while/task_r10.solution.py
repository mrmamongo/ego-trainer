def task_r10_sum_squares(n):
    total = 0
    for i in range(1, n + 1):
        total = total + i * i
    return total
