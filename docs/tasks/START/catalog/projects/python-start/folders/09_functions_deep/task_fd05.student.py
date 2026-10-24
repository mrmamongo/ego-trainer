def task_fd05_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | total = 100
    #   2 | def bump(total):
    #   3 |     total = total + 1
    #   4 |     return total
    #   5 | def read_total():
    #   6 |     return total
    #   7 | a = bump(total)
    #   8 | b = bump(5)
    #   9 | c = read_total()
    #  10 | total = 7
    #  11 | d = read_total()
    #
    # a_after_7: значение a после строки 7
    # b_after_8: значение b после строки 8
    # c_after_9: значение c после строки 9
    # d_after_11: значение d после строки 11
    # total_after_9: значение глобальной total после строки 9

    a_after_7 = None
    b_after_8 = None
    c_after_9 = None
    d_after_11 = None
    total_after_9 = None

    # Ниже ничего не меняй: это рамка для проверки.
    return a_after_7, b_after_8, c_after_9, d_after_11, total_after_9
