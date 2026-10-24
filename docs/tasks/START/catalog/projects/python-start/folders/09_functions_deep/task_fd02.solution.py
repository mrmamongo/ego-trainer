def is_even(n):
    return n % 2 == 0


def task_fd02_count_even(nums):
    count = 0
    for n in nums:
        if is_even(n):
            count = count + 1
    return count
