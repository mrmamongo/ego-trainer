def count_items(nums):
    count = 0
    for n in nums:
        count = count + 1
    return count


def sum_items(nums):
    total = 0
    for n in nums:
        total = total + n
    return total


def task_fd15_stats(nums):
    count = count_items(nums)
    if count == 0:
        return 0, 0, 0
    total = sum_items(nums)
    return count, total, total / count
