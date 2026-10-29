def task_cl10_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Player:
    #   2 |     def __init__(self, hp):
    #   3 |         self.hp = hp
    #   4 |     def is_alive(self):
    #   5 |         return self.hp > 0
    #   6 |     def hit(self, damage):
    #   7 |         self.hp = self.hp - damage
    #   8 |         return self.is_alive()
    #   9 | p = Player(10)
    #  10 | a = p.is_alive()
    #  11 | b = p.hit(4)
    #  12 | c = p.hp
    #  13 | d = p.hit(6)
    #  14 | e = p.hp
    #  15 | f = p.is_alive()
    #
    # a_value: что вернул p.is_alive() в строке 10 (True или False)
    # b_value: что вернул p.hit(4) в строке 11 (True или False)
    # c_value: p.hp после строки 11
    # d_value: что вернул p.hit(6) в строке 13 (True или False)
    # e_value: p.hp после строки 13
    # f_value: что вернул p.is_alive() в строке 15 (True или False)

    a_value = True
    b_value = True
    c_value = 6
    d_value = False
    e_value = 0
    f_value = False

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, e_value, f_value
