def task_r14_digit_sum(n):
    total = 0
    while n > 0:
        digit = n % 10
        total = total + digit
        n = n // 10
    return total
