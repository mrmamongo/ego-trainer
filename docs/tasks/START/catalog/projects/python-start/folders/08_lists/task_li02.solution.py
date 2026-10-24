def task_li02_swap_ends(nums):
    result = []
    for number in nums:
        result.append(number)
    if len(result) >= 2:
        first = result[0]
        result[0] = result[-1]
        result[-1] = first
    return result
