# Сейчас функция работает по старому правилу: складывает всё до нуля.
def task_fd10_sum_until_zero(nums):
    total = 0
    for n in nums:
        if n == 0:
            break
        total = total + n
    return total
