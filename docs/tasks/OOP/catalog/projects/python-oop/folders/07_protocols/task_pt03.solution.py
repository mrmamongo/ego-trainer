def task_pt03_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | log = []
    #   2 | def gen():
    #   3 |     log.append("старт")
    #   4 |     yield 1
    #   5 |     log.append("середина")
    #   6 |     yield 2
    #   7 |     log.append("финиш")
    #   8 | g = gen()
    #   9 | n0 = len(log)
    #  10 | v = next(g)
    #  11 | n1 = len(log)
    #  12 | w = next(g)
    #  13 | n2 = len(log)
    #  14 | rest = list(g)
    #  15 | n3 = len(log)
    #  16 | last = log[-1]
    #  17 | after = next(g, "пусто")
    #
    # len_before: значение n0, число (строка 9)
    # first_value: значение v, число (строка 10)
    # len_after_one: значение n1, число (строка 11)
    # second_value: значение w, число (строка 12)
    # len_after_two: значение n2, число (строка 13)
    # rest_len: сколько элементов в rest, число (строка 14)
    # len_end: значение n3, число (строка 15)
    # last_entry: значение last, строка (строка 16)
    # after_end: значение after, строка (строка 17)

    len_before = 0
    first_value = 1
    len_after_one = 1
    second_value = 2
    len_after_two = 2
    rest_len = 0
    len_end = 3
    last_entry = 'финиш'
    after_end = 'пусто'

    # Ниже ничего не меняй: это рамка для проверки.
    return len_before, first_value, len_after_one, second_value, len_after_two, rest_len, len_end, last_entry, after_end
