def task_mo03_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Score:
    #   2 |     def __init__(self, points):
    #   3 |         self.points = points
    #   4 |     def __add__(self, other):
    #   5 |         if not isinstance(other, Score):
    #   6 |             return NotImplemented
    #   7 |         return Score(self.points + other.points)
    #   8 |     def __radd__(self, other):
    #   9 |         if other == 0:
    #  10 |             return self
    #  11 |         return NotImplemented
    #  12 | a = Score(5)
    #  13 | b = Score(7)
    #  14 | c = a + b
    #  15 | s = sum([a, b])
    #  16 | t = sum([])
    #  17 | u = sum([a])
    #  18 | try:
    #  19 |     v = 3 + a
    #  20 |     status = "ok"
    #  21 | except TypeError:
    #  22 |     status = "TypeError"
    #
    # c_points: значение c.points (строка 14)
    # s_points: значение s.points (строка 15)
    # empty_sum: значение t (строка 16): сумма пустого списка
    # u_is_a: значение u is a (строка 17), True или False
    # a_points: значение a.points после всех строк
    # status: значение status после блока try (строки 18-22)

    c_points = None
    s_points = None
    empty_sum = None
    u_is_a = None
    a_points = None
    status = None

    # Ниже ничего не меняй: это рамка для проверки.
    return c_points, s_points, empty_sum, u_is_a, a_points, status
