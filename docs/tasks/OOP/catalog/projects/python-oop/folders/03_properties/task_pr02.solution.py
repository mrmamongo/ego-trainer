def task_pr02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Temperature:
    #   2 |     def __init__(self, celsius):
    #   3 |         self._celsius = celsius
    #   4 |     def cool(self, degrees):
    #   5 |         self._celsius = self._celsius - degrees
    #   6 |     @property
    #   7 |     def fahrenheit(self):
    #   8 |         return self._celsius * 9 / 5 + 32
    #   9 |     @property
    #  10 |     def celsius(self):
    #  11 |         return self._celsius
    #  12 | t = Temperature(100)
    #  13 | a = t.fahrenheit
    #  14 | t.cool(100)
    #  15 | b = t.celsius
    #  16 | c = t.fahrenheit
    #  17 | t.cool(40)
    #  18 | d = t.fahrenheit
    #  19 | u = Temperature(-40)
    #  20 | e = u.fahrenheit == d
    #
    # a_value: значение a (строка 13)
    # celsius_now: значение b (строка 15)
    # f_zero: значение c (строка 16)
    # f_minus: значение d (строка 18)
    # same: значение e (строка 20), True или False

    a_value = 212.0
    celsius_now = 0
    f_zero = 32.0
    f_minus = -40.0
    same = True

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, celsius_now, f_zero, f_minus, same
