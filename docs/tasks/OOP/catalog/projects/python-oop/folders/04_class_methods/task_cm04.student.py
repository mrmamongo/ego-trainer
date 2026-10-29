def task_cm04_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Score:
    #   2 |     total = 0
    #   3 |     def __init__(self, points):
    #   4 |         self.points = points
    #   5 |     @staticmethod
    #   6 |     def bonus(points):
    #   7 |         return points * 2
    #   8 |     @classmethod
    #   9 |     def double(cls, points):
    #  10 |         cls.total = cls.total + 1
    #  11 |         return cls(cls.bonus(points))
    #  12 | a = Score.bonus(5)
    #  13 | p = Score.double(3)
    #  14 | q = Score.double(10)
    #  15 | b = p.points + q.points
    #  16 | c = Score.total
    #  17 | d = p is q
    #  18 | e = p.bonus(1)
    #
    # a_value: что вернул Score.bonus(5) в строке 12
    # b_value: p.points + q.points в строке 15
    # c_value: Score.total в строке 16
    # d_value: один ли это объект: p is q (True или False)
    # e_value: что вернул p.bonus(1) в строке 18
    a_value = None
    b_value = None
    c_value = None
    d_value = None
    e_value = None
    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, e_value
