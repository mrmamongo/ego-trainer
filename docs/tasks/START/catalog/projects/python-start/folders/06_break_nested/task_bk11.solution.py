def task_bk11_is_prime(n):
    if n < 2:
        return False
    for d in range(2, n):
        if n % d == 0:
            break
    else:
        return True
    return False
