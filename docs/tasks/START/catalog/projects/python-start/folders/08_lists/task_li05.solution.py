def task_li05_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | a = [1, 2]
    #   2 | b = a
    #   3 | b.append(3)
    #   4 | c = a[:]
    #   5 | c.append(4)
    #   6 | a[0] = 9
    #
    # len_a: len(a) после строки 6
    # len_b: len(b) после строки 6
    # len_c: len(c) после строки 6
    # b_first: b[0] после строки 6
    # c_first: c[0] после строки 6

    len_a = 3
    len_b = 3
    len_c = 4
    b_first = 9
    c_first = 1

    # Ниже ничего не меняй: это рамка для проверки.
    return len_a, len_b, len_c, b_first, c_first
