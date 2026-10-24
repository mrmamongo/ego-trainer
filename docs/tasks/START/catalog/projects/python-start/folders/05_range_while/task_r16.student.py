def task_r16_digit_sum(n):
    total = 0
    while n > 9:
        total = total + n % 10
        n = n // 10
    return total
