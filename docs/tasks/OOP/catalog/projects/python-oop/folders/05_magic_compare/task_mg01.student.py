def task_mg01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Coin:
    #   2 |     def __init__(self, value):
    #   3 |         self.value = value
    #   4 |     def __repr__(self):
    #   5 |         return f"Coin({self.value})"
    #   6 |     def __str__(self):
    #   7 |         return f"{self.value} монет"
    #   8 | class Gem:
    #   9 |     def __init__(self, name):
    #  10 |         self.name = name
    #  11 |     def __repr__(self):
    #  12 |         return f"Gem('{self.name}')"
    #  13 | c = Coin(5)
    #  14 | g = Gem("рубин")
    #  15 | a = repr(c)
    #  16 | b = str(c)
    #  17 | d = f"{c}"
    #  18 | e = str([c])
    #  19 | h = str(g)
    #  20 | k = f"{g} и {c}"
    #
    # repr_coin: значение a, строка (строка 15)
    # str_coin: значение b, строка (строка 16)
    # fstring_coin: значение d, строка (строка 17)
    # list_text: значение e, строка (строка 18): список с монетой внутри
    # str_gem: значение h, строка (строка 19): у Gem нет __str__
    # mixed: значение k, строка (строка 20)

    repr_coin = None
    str_coin = None
    fstring_coin = None
    list_text = None
    str_gem = None
    mixed = None

    # Ниже ничего не меняй: это рамка для проверки.
    return repr_coin, str_coin, fstring_coin, list_text, str_gem, mixed
