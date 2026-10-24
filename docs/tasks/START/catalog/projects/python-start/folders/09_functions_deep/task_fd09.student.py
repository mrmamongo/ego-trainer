# Сейчас функция работает по старому правилу: возвращает само число.
def task_fd09_first_negative(nums):
    for n in nums:
        if n < 0:
            return n
    return 0
