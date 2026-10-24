def task_li07_remove_all(nums, x):
    result = []
    for number in nums:
        if number != x:
            result.append(number)
    return result
