def task_ts02_min_max(nums):
    low = nums[0]
    high = nums[0]
    for n in nums:
        if n < low:
            low = n
        if n > high:
            high = n
    return low, high
