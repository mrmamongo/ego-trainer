def task_pr01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Wallet:
    #   2 |     def __init__(self, money):
    #   3 |         self._money = money
    #   4 |     def add(self, k):
    #   5 |         self._money = self._money + k
    #   6 |     def total(self):
    #   7 |         return self._money
    #   8 | w = Wallet(100)
    #   9 | w.add(50)
    #  10 | a = w.total()
    #  11 | w._money = 10
    #  12 | b = w.total()
    #  13 | w.add(5)
    #  14 | c = w._money
    #  15 | v = Wallet(1)
    #  16 | d = w.total() + v.total()
    #  17 | e = w.total() == w._money
    #
    # a_value: значение a (строка 10)
    # after_hack: значение b (строка 12), после записи снаружи
    # direct_read: значение c (строка 14)
    # sum_total: значение d (строка 16)
    # same: значение e (строка 17), True или False

    a_value = 150
    after_hack = 10
    direct_read = 15
    sum_total = 16
    same = True

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, after_hack, direct_read, sum_total, same
