def task_pr05_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Player:
    #   2 |     def __init__(self, max_hp):
    #   3 |         self.max_hp = max_hp
    #   4 |         self._hp = max_hp
    #   5 |     @property
    #   6 |     def hp(self):
    #   7 |         return self._hp
    #   8 |     @hp.setter
    #   9 |     def hp(self, value):
    #  10 |         if value < 0:
    #  11 |             value = 0
    #  12 |         if value > self.max_hp:
    #  13 |             value = self.max_hp
    #  14 |         self._hp = value
    #  15 | p = Player(50)
    #  16 | p.hp = 70
    #  17 | a = p.hp
    #  18 | p.hp = 20
    #  19 | p.hp = p.hp - 30
    #  20 | b = p.hp
    #  21 | p._hp = 99
    #  22 | c = p.hp
    #  23 | p.hp = 10
    #  24 | d = p._hp
    #  25 | e = p.max_hp
    #
    # after_big: значение a (строка 17)
    # after_minus: значение b (строка 20)
    # after_hack: значение c (строка 22)
    # stored: значение d (строка 24)
    # limit: значение e (строка 25)

    after_big = 50
    after_minus = 0
    after_hack = 99
    stored = 10
    limit = 50

    # Ниже ничего не меняй: это рамка для проверки.
    return after_big, after_minus, after_hack, stored, limit
