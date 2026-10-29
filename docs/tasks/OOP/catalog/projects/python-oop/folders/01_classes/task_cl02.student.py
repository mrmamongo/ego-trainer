def task_cl02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Player:
    #   2 |     def __init__(self, name, hp):
    #   3 |         self.name = name
    #   4 |         self.hp = hp
    #   5 |     def hit(self, damage):
    #   6 |         self.hp = self.hp - damage
    #   7 |     def after_hit(self, damage):
    #   8 |         return self.hp - damage
    #   9 | p = Player("Аня", 30)
    #  10 | p.hit(10)
    #  11 | a = p.hp
    #  12 | b = p.after_hit(5)
    #  13 | c = p.hp
    #  14 | d = p.hit(1)
    #  15 | e = p.hp
    #
    # a_value: p.hp в строке 11
    # b_value: что вернул p.after_hit(5) в строке 12
    # c_value: p.hp после строки 12
    # d_is_none: True, если после строки 14 в d лежит None, иначе False
    # e_value: p.hp после строки 14

    a_value = None
    b_value = None
    c_value = None
    d_is_none = None
    e_value = None

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_is_none, e_value
