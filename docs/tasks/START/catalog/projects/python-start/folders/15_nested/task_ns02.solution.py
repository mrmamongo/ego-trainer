def task_ns02_sum_list(numbers):
    if len(numbers) == 0:
        return 0
    return numbers[0] + task_ns02_sum_list(numbers[1:])
