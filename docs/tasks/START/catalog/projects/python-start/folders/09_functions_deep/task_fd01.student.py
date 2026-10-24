def task_fd01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def double(n):
    #   2 |     return n * 2
    #   3 | def add_bonus(x):
    #   4 |     return double(x) + 1
    #   5 | a = double(3)
    #   6 | b = add_bonus(a)
    #   7 | c = add_bonus(double(2))
    #
    # a_after_5: значение a после строки 5
    # b_after_6: значение b после строки 6
    # c_after_7: значение c после строки 7
    # double_calls_in_line_7: сколько раз за строку 7 вызвали double (считай и вызовы внутри add_bonus)

    a_after_5 = None
    b_after_6 = None
    c_after_7 = None
    double_calls_in_line_7 = None

    # Ниже ничего не меняй: это рамка для проверки.
    return a_after_5, b_after_6, c_after_7, double_calls_in_line_7
