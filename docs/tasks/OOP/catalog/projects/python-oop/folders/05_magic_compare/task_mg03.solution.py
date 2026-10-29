def task_mg03_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Version:
    #   2 |     def __init__(self, major, minor):
    #   3 |         self.major = major
    #   4 |         self.minor = minor
    #   5 |     def __lt__(self, other):
    #   6 |         return (self.major, self.minor) < (other.major, other.minor)
    #   7 | a = Version(1, 9)
    #   8 | b = Version(1, 10)
    #   9 | c = Version(0, 99)
    #  10 | r1 = a < b
    #  11 | r2 = b < a
    #  12 | r3 = a > b
    #  13 | r4 = "1.9" < "1.10"
    #  14 | ordered = sorted([b, a, c])
    #  15 | r5 = ordered[0].minor
    #  16 | r6 = ordered[-1].minor
    #
    # a_less_b: значение r1 (строка 10, True или False)
    # b_less_a: значение r2 (строка 11, True или False)
    # a_greater_b: значение r3 (строка 12, True или False)
    # text_less: значение r4: сравнение строк (строка 13, True или False)
    # first_minor: r5: minor первой версии в отсортированном списке (строка 15)
    # last_minor: r6: minor последней версии в отсортированном списке (строка 16)

    a_less_b = True
    b_less_a = False
    a_greater_b = False
    text_less = False
    first_minor = 99
    last_minor = 10

    # Ниже ничего не меняй: это рамка для проверки.
    return a_less_b, b_less_a, a_greater_b, text_less, first_minor, last_minor
