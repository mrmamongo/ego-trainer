def task_cl05_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Player:
    #   2 |     def __init__(self, name, hp):
    #   3 |         self.name = name
    #   4 |         self.hp = hp
    #   5 | a = Player("Аня", 30)
    #   6 | b = a
    #   7 | b.hp = 10
    #   8 | c = a.hp
    #   9 | d = Player("Аня", 10)
    #  10 | e = a is b
    #  11 | f = a is d
    #  12 | g = a == d
    #  13 | h = d.hp == a.hp
    #
    # c_value: значение c (строка 8)
    # e_value: значение e, True или False (строка 10)
    # f_value: значение f, True или False (строка 11)
    # g_value: значение g, True или False (строка 12)
    # h_value: значение h, True или False (строка 13)

    c_value = None
    e_value = None
    f_value = None
    g_value = None
    h_value = None

    # Ниже ничего не меняй: это рамка для проверки.
    return c_value, e_value, f_value, g_value, h_value
