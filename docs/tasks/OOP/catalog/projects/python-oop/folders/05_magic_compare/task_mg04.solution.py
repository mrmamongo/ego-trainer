def task_mg04_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Card:
    #   2 |     def __init__(self, rank, suit):
    #   3 |         self.rank = rank
    #   4 |         self.suit = suit
    #   5 |     def __eq__(self, other):
    #   6 |         return self.rank == other.rank and self.suit == other.suit
    #   7 |     def __hash__(self):
    #   8 |         return hash((self.rank, self.suit))
    #   9 | class Token:
    #  10 |     pass
    #  11 | hand = {Card("Q", "червы"), Card("K", "пики"), Card("Q", "червы")}
    #  12 | n_hand = len(hand)
    #  13 | has_king = Card("K", "пики") in hand
    #  14 | has_ace = Card("A", "пики") in hand
    #  15 | tokens = {Token(), Token()}
    #  16 | n_tokens = len(tokens)
    #  17 | stock = {}
    #  18 | stock[Card("7", "бубны")] = 1
    #  19 | stock[Card("7", "бубны")] = stock[Card("7", "бубны")] + 1
    #  20 | n_stock = len(stock)
    #  21 | seven = stock[Card("7", "бубны")]
    #
    # n_hand: значение n_hand, число (строка 12)
    # has_king: значение has_king (строка 13, True или False)
    # has_ace: значение has_ace (строка 14, True или False)
    # n_tokens: значение n_tokens (строка 16): у Token нет ни __eq__, ни __hash__
    # n_stock: значение n_stock (строка 20)
    # seven: значение seven (строка 21)

    n_hand = 2
    has_king = True
    has_ace = False
    n_tokens = 2
    n_stock = 1
    seven = 2

    # Ниже ничего не меняй: это рамка для проверки.
    return n_hand, has_king, has_ace, n_tokens, n_stock, seven
