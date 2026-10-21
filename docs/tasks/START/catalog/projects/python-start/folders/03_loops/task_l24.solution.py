def task_l24_count_in_range(numbers, low, high):
    count = 0
    for number in numbers:
        if number >= low and number <= high:
            count = count + 1
    return count
