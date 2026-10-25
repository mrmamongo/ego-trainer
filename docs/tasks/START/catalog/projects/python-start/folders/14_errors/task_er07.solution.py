def task_er07_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def inner(x):
    #   2 |     return 10 // x
    #   3 | def middle(x):
    #   4 |     try:
    #   5 |         return inner(x) + 1
    #   6 |     except KeyError:
    #   7 |         return -1
    #   8 | def outer(x):
    #   9 |     try:
    #  10 |         return middle(x)
    #  11 |     except ZeroDivisionError:
    #  12 |         return -2
    #  13 | a = outer(5)
    #  14 | b = outer(0)
    #  15 | c = outer(3)
    #
    # a_value: чему равно a после строки 13
    # b_value: чему равно b после строки 14
    # c_value: чему равно c после строки 15
    # b_caught_in: в какой функции поймана ошибка вызова outer(0): "inner", "middle" или "outer"

    a_value = 3
    b_value = -2
    c_value = 4
    b_caught_in = "outer"

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, b_caught_in
