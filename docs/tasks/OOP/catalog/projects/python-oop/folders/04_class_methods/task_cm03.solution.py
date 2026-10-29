def task_cm03_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Item:
    #   2 |     created = 0
    #   3 |     def __init__(self, name):
    #   4 |         self.name = name
    #   5 |         Item.created = Item.created + 1
    #   6 | a = Item("меч")
    #   7 | b = Item("щит")
    #   8 | x = Item.created
    #   9 | y = a.created
    #  10 | a.created = 10
    #  11 | z = Item.created
    #  12 | w = b.created
    #  13 | v = a.created
    #
    # x_value: Item.created в строке 8
    # y_value: a.created в строке 9
    # z_value: Item.created в строке 11
    # w_value: b.created в строке 12
    # v_value: a.created в строке 13
    x_value = 2
    y_value = 2
    z_value = 2
    w_value = 2
    v_value = 10
    # Ниже ничего не меняй: это рамка для проверки.
    return x_value, y_value, z_value, w_value, v_value
