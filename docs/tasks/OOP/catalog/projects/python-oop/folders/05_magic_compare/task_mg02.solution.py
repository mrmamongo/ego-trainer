def task_mg02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Card:
    #   2 |     def __init__(self, rank, suit):
    #   3 |         self.rank = rank
    #   4 |         self.suit = suit
    #   5 |     def __eq__(self, other):
    #   6 |         if not isinstance(other, Card):
    #   7 |             return NotImplemented
    #   8 |         return self.rank == other.rank and self.suit == other.suit
    #   9 | a = Card("Q", "червы")
    #  10 | b = Card("Q", "червы")
    #  11 | c = a
    #  12 | d = Card("Q", "пики")
    #  13 | r1 = a == b
    #  14 | r2 = a is b
    #  15 | r3 = a == d
    #  16 | r4 = a == "Q"
    #  17 | r5 = a != d
    #  18 | r6 = [a, d].count(b)
    #
    # equal_ab: значение r1 (строка 13, True или False)
    # same_ab: значение r2 (строка 14, True или False)
    # equal_ad: значение r3 (строка 15, True или False)
    # equal_text: значение r4: карта и строка (строка 16, True или False)
    # not_equal_ad: значение r5 (строка 17, True или False)
    # count_b: значение r6, число (строка 18)

    equal_ab = True
    same_ab = False
    equal_ad = False
    equal_text = False
    not_equal_ad = True
    count_b = 1

    # Ниже ничего не меняй: это рамка для проверки.
    return equal_ab, same_ab, equal_ad, equal_text, not_equal_ad, count_b
