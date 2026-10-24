def task_fd10_sum_until_zero(nums):
    total = 0
    for n in nums:
        if n == 0:
            break
        if n < 0:
            continue
        total = total + n
    return total
