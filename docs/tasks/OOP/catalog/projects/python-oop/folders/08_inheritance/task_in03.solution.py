def task_in03_lookup():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Unit:
    #   2 |     speed = 3
    #   3 |     def __init__(self, name):
    #   4 |         self.name = name
    #   5 | class Horseman(Unit):
    #   6 |     speed = 8
    #   7 | class Scout(Unit):
    #   8 |     pass
    #   9 | h = Horseman("Ян")
    #  10 | s = Scout("Лис")
    #  11 | a = h.speed
    #  12 | b = s.speed
    #  13 | s.speed = 5
    #  14 | c = s.speed
    #  15 | d = Scout("Рысь").speed
    #  16 | e = Unit.speed
    #
    # a_value: значение a (строка 11)
    # b_value: значение b (строка 12)
    # c_value: значение c (строка 14)
    # d_value: значение d (строка 15)
    # e_value: значение e (строка 16)

    a_value = 8
    b_value = 3
    c_value = 5
    d_value = 3
    e_value = 3

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, e_value
