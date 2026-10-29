def task_cl13_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Item:
    #   2 |     def __init__(self, title):
    #   3 |         self.title = title
    #   4 | a = Item("меч")
    #   5 | b = Item("меч")
    #   6 | items = [a, b, a]
    #   7 | items[0].title = "щит"
    #   8 | n = len(items)
    #   9 | x = items[2].title
    #  10 | y = items[1].title
    #  11 | z = items[0] is items[2]
    #  12 | w = items[0] == b
    #
    # n_value: значение n (строка 8)
    # x_value: значение x (строка 9)
    # y_value: значение y (строка 10)
    # z_value: значение z, True или False (строка 11)
    # w_value: значение w, True или False (строка 12)

    n_value = 3
    x_value = 'щит'
    y_value = 'меч'
    z_value = True
    w_value = False

    # Ниже ничего не меняй: это рамка для проверки.
    return n_value, x_value, y_value, z_value, w_value
