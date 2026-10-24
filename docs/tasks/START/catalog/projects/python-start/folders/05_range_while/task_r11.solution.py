def task_r11_powers_of_two(k):
    result = []
    power = 1
    for i in range(k):
        result.append(power)
        power = power * 2
    return result
