def task_l23_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #    1 | def stats(numbers):
    #    2 |     a = 0
    #    3 |     b = 0
    #    4 |     c = []
    #    5 |     for d in numbers:
    #    6 |         a = a + d
    #    7 |         if d > 10:
    #    8 |             b = b + 1
    #    9 |             c.append(d)
    #   10 |     return a, b, c
    #
    # role_of_a, role_of_b, role_of_c, role_of_d: роль переменных a, b, c, d.
    # Допустимые ответы (строки): "накопитель", "счётчик", "сборщик", "флаг", "лучший", "текущий элемент".

    role_of_a = None
    role_of_b = None
    role_of_c = None
    role_of_d = None

    # Ниже ничего не меняй: это рамка для проверки.
    return role_of_a, role_of_b, role_of_c, role_of_d
