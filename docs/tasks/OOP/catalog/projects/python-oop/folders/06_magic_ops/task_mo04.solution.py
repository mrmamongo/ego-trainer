def task_mo04_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Cart:
    #   2 |     def __init__(self, items):
    #   3 |         self.items = items
    #   4 |     def __len__(self):
    #   5 |         return len(self.items)
    #   6 | class Box:
    #   7 |     def __init__(self, items):
    #   8 |         self.items = items
    #   9 |     def __len__(self):
    #  10 |         return len(self.items)
    #  11 |     def __bool__(self):
    #  12 |         return True
    #  13 | class Bag:
    #  14 |     def __init__(self, items):
    #  15 |         self.items = items
    #  16 |     def __contains__(self, item):
    #  17 |         return item in self.items
    #  18 | c = Cart([])
    #  19 | b = Box([])
    #  20 | g = Bag(["меч", "щит"])
    #  21 | x = bool(c)
    #  22 | y = bool(b)
    #  23 | z = "щит" in g
    #  24 | w = "лук" in g
    #  25 | v = bool(Bag([]))
    #
    # cart_empty: значение x (строка 21)
    # box_empty: значение y (строка 22)
    # has_shield: значение z (строка 23)
    # has_bow: значение w (строка 24)
    # empty_bag: значение v (строка 25): у Bag нет ни __bool__, ни __len__

    cart_empty = False
    box_empty = True
    has_shield = True
    has_bow = False
    empty_bag = True

    # Ниже ничего не меняй: это рамка для проверки.
    return cart_empty, box_empty, has_shield, has_bow, empty_bag
