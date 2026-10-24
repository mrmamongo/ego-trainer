def count_big(numbers, limit):
    count = 0
    for n in numbers:
        if n > limit:
            count = count + 1
    return count


def task_fd06_report(first, second, limit):
    return count_big(first, limit), count_big(second, limit)
