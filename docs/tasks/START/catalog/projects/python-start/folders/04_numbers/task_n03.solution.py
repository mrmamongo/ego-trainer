def task_n03_digit_sum3(n):
    units = n % 10
    tens = n // 10 % 10
    hundreds = n // 100
    return units + tens + hundreds
