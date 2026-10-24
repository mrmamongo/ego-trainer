def task_li16_unique_in_order(nums):
    result = []
    for number in nums:
        if number not in result:
            result.append(number)
    return result
