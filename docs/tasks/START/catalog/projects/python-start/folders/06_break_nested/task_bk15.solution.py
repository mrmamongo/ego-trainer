def task_bk15_count_pairs_with_sum(a, b, target):
    count = 0
    for x in a:
        for y in b:
            if x + y == target:
                count = count + 1
    return count
