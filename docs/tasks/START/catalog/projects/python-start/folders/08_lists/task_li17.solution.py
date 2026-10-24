def task_li17_chunk(nums, size):
    result = []
    for start in range(0, len(nums), size):
        result.append(nums[start:start + size])
    return result
