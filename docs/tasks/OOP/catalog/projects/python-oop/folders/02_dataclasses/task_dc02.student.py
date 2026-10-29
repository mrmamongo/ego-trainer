def task_dc02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | from dataclasses import dataclass, field
    #   2 | @dataclass
    #   3 | class Quest:
    #   4 |     title: str
    #   5 |     reward: int = 10
    #   6 |     tags: list = field(default_factory=list)
    #   7 | a = Quest("Волки")
    #   8 | b = Quest("Лис", 50)
    #   9 | a.tags.append("бой")
    #  10 | d = Quest("Дракон")
    #  11 | r1 = a.reward
    #  12 | r2 = b.reward
    #  13 | r3 = len(a.tags)
    #  14 | r4 = len(d.tags)
    #  15 | r5 = a.tags is d.tags
    #  16 | r6 = a == Quest("Волки", 10, ["бой"])
    #
    # a_reward: значение r1 (строка 11)
    # b_reward: значение r2 (строка 12)
    # a_tags: значение r3, сколько тегов у a (строка 13)
    # d_tags: значение r4, сколько тегов у d (строка 14)
    # same_list: значение r5, общий ли это список (строка 15, True или False)
    # a_equals_copy: значение r6 (строка 16, True или False)

    a_reward = None
    b_reward = None
    a_tags = None
    d_tags = None
    same_list = None
    a_equals_copy = None

    # Ниже ничего не меняй: это рамка для проверки.
    return a_reward, b_reward, a_tags, d_tags, same_list, a_equals_copy
