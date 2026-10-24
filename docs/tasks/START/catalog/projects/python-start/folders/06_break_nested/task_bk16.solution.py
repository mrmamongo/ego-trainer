def task_bk16_has_common(a, b):
    for x in a:
        for y in b:
            if x == y:
                return True
    return False
