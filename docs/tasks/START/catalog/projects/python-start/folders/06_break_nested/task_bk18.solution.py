def task_bk18_dice_ways(total):
    count = 0
    for a in range(1, 7):
        for b in range(1, 7):
            if a + b == total:
                count = count + 1
    return count
