def task_r07_is_prime(n):
    if n < 2:
        return False
    is_prime = True
    for d in range(2, n):
        if n % d == 0:
            is_prime = False
    return is_prime
