def task_cl01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Player:
    #   2 |     def __init__(self, name, hp):
    #   3 |         self.name = name
    #   4 |         self.hp = hp
    #   5 | hero = Player("Аня", 30)
    #   6 | boss = Player("Орк", 80)
    #   7 | a = hero.hp
    #   8 | hero.hp = 25
    #   9 | b = hero.hp
    #  10 | c = boss.hp
    #  11 | d = boss.name
    #  12 | e = hero.hp + boss.hp
    #
    # a_value: hero.hp в строке 7
    # hero_hp: hero.hp после строки 8
    # boss_hp: boss.hp (строка 10)
    # boss_name: boss.name (строка 11)
    # sum_hp: значение e (строка 12)

    a_value = None
    hero_hp = None
    boss_hp = None
    boss_name = None
    sum_hp = None

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, hero_hp, boss_hp, boss_name, sum_hp
