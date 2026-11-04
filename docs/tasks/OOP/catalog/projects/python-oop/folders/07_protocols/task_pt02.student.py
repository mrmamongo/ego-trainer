def task_pt02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Countdown:
    #   2 |     def __init__(self, start):
    #   3 |         self.current = start
    #   4 |     def __iter__(self):
    #   5 |         return self
    #   6 |     def __next__(self):
    #   7 |         if self.current <= 0:
    #   8 |             raise StopIteration
    #   9 |         value = self.current
    #  10 |         self.current -= 1
    #  11 |         return value
    #  12 | c = Countdown(3)
    #  13 | first = list(c)
    #  14 | second = list(c)
    #  15 | t = Countdown(2)
    #  16 | x = next(t)
    #  17 | y = next(t)
    #  18 | z = next(t, "конец")
    #  19 | cur = t.current
    #  20 | same = iter(t) is t
    #
    # first_sum: сумма чисел в first, число (строка 13)
    # second_len: сколько элементов в second, число (строка 14)
    # x_value: значение x, число (строка 16)
    # y_value: значение y, число (строка 17)
    # z_value: значение z, строка (строка 18)
    # current_now: значение cur, число (строка 19)
    # is_iterator: значение same, True или False (строка 20)

    first_sum = None
    second_len = None
    x_value = None
    y_value = None
    z_value = None
    current_now = None
    is_iterator = None

    # Ниже ничего не меняй: это рамка для проверки.
    return first_sum, second_len, x_value, y_value, z_value, current_now, is_iterator
