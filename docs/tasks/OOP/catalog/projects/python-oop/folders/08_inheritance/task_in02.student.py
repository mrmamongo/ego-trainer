def task_in02_super():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Unit:
    #   2 |     def __init__(self, name, hp):
    #   3 |         self.name = name
    #   4 |         self.hp = hp
    #   5 |     def describe(self):
    #   6 |         return self.name + ":" + str(self.hp)
    #   7 | class Mage(Unit):
    #   8 |     def __init__(self, name, hp, mana):
    #   9 |         super().__init__(name, hp)
    #  10 |         self.mana = mana
    #  11 |     def describe(self):
    #  12 |         return super().describe() + "/" + str(self.mana)
    #  13 | class Archer(Unit):
    #  14 |     def describe(self):
    #  15 |         return "лучник " + self.name
    #  16 | m = Mage("Мерлин", 30, 50)
    #  17 | a = m.hp
    #  18 | b = m.describe()
    #  19 | x = Archer("Робин", 25)
    #  20 | c = x.describe()
    #  21 | d = x.hp
    #  22 | e = m.mana + m.hp
    #
    # a_value: значение a (строка 17)
    # b_value: значение b (строка 18)
    # c_value: значение c (строка 20)
    # d_value: значение d (строка 21)
    # e_value: значение e (строка 22)

    a_value = None
    b_value = None
    c_value = None
    d_value = None
    e_value = None

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, e_value
