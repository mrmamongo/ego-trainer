def task_r22_gcd(a, b):
    while b != 0:
        remainder = a % b
        a = b
        b = remainder
    return a
