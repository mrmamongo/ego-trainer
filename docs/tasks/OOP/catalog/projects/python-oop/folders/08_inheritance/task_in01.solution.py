def task_in01_inherit():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Unit:
    #   2 |     def __init__(self, name, hp):
    #   3 |         self.name = name
    #   4 |         self.hp = hp
    #   5 |     def attack(self):
    #   6 |         return 5
    #   7 |     def is_alive(self):
    #   8 |         return self.hp > 0
    #   9 | class Warrior(Unit):
    #  10 |     def attack(self):
    #  11 |         return 12
    #  12 | u = Unit("Тень", 0)
    #  13 | w = Warrior("Грок", 40)
    #  14 | a = u.attack()
    #  15 | b = w.attack()
    #  16 | c = w.name
    #  17 | d = w.is_alive()
    #  18 | e = u.is_alive()
    #
    # a_value: значение a (строка 14)
    # b_value: значение b (строка 15)
    # c_value: значение c (строка 16)
    # d_value: значение d, True или False (строка 17)
    # e_value: значение e, True или False (строка 18)

    a_value = 5
    b_value = 12
    c_value = 'Грок'
    d_value = True
    e_value = False

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, e_value
