def task_fn15_max3(a, b, c):
    best = a
    if b > best:
        best = b
    if c > best:
        best = c
    return best
