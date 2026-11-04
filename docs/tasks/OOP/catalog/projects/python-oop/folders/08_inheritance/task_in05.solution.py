def task_in05_isinstance():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Unit:
    #   2 |     pass
    #   3 | class Warrior(Unit):
    #   4 |     pass
    #   5 | class Mage(Unit):
    #   6 |     pass
    #   7 | class Paladin(Warrior):
    #   8 |     pass
    #   9 | p = Paladin()
    #  10 | a = isinstance(p, Paladin)
    #  11 | b = isinstance(p, Warrior)
    #  12 | c = isinstance(p, Mage)
    #  13 | d = issubclass(Mage, Unit)
    #  14 | e = issubclass(Unit, Warrior)
    #  15 | f = type(p) == Warrior
    #
    # a_value: значение a, True или False (строка 10)
    # b_value: значение b, True или False (строка 11)
    # c_value: значение c, True или False (строка 12)
    # d_value: значение d, True или False (строка 13)
    # e_value: значение e, True или False (строка 14)
    # f_value: значение f, True или False (строка 15)

    a_value = True
    b_value = True
    c_value = False
    d_value = True
    e_value = False
    f_value = False

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, e_value, f_value
