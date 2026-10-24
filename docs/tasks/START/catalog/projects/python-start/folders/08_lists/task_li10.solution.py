def task_li10_insert_sorted(nums, x):
    pos = 0
    while pos < len(nums) and nums[pos] < x:
        pos = pos + 1
    return nums[:pos] + [x] + nums[pos:]
