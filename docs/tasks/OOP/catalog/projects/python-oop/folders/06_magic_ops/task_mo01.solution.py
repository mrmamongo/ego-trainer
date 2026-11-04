def task_mo01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Vector2:
    #   2 |     def __init__(self, x, y):
    #   3 |         self.x = x
    #   4 |         self.y = y
    #   5 |     def __add__(self, other):
    #   6 |         return Vector2(self.x + other.x, self.y + other.y)
    #   7 |     def __mul__(self, k):
    #   8 |         return Vector2(self.x * k, self.y * k)
    #   9 | a = Vector2(1, 2)
    #  10 | b = Vector2(10, 20)
    #  11 | c = a + b
    #  12 | d = c * 2
    #  13 | e = a + Vector2(0, 0)
    #
    # c_x: значение c.x (строка 11)
    # c_y: значение c.y (строка 11)
    # d_y: значение d.y (строка 12)
    # a_x: значение a.x после всех строк
    # e_x: значение e.x (строка 13)
    # e_is_a: значение выражения e is a (True или False)

    c_x = 11
    c_y = 22
    d_y = 44
    a_x = 1
    e_x = 1
    e_is_a = False

    # Ниже ничего не меняй: это рамка для проверки.
    return c_x, c_y, d_y, a_x, e_x, e_is_a
