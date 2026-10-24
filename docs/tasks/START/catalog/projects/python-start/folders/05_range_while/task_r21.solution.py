def task_r21_digital_root(n):
    while n > 9:
        total = 0
        while n > 0:
            total = total + n % 10
            n = n // 10
        n = total
    return n
