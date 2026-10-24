def task_bk14_table_sum(n):
    total = 0
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            total = total + i * j
    return total
