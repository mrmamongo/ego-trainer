def task_r15_reverse_number(n):
    result = 0
    while n > 0:
        digit = n % 10
        result = result * 10 + digit
        n = n // 10
    return result
