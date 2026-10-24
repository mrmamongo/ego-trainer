def task_li08_rotate_left(nums, k):
    if len(nums) == 0:
        return []
    shift = k % len(nums)
    return nums[shift:] + nums[:shift]
