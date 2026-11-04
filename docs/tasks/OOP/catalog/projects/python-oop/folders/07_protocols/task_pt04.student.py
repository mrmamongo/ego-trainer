def task_pt04_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | events = []
    #   2 | class Guard:
    #   3 |     def __init__(self, hide):
    #   4 |         self.hide = hide
    #   5 |     def __enter__(self):
    #   6 |         events.append("вход")
    #   7 |         return self
    #   8 |     def __exit__(self, exc_type, exc, tb):
    #   9 |         events.append("выход")
    #  10 |         return self.hide
    #  11 | with Guard(True):
    #  12 |     events.append("тело")
    #  13 |     raise ValueError("x")
    #  14 | events.append("после")
    #  15 | a = len(events)
    #  16 | try:
    #  17 |     with Guard(False):
    #  18 |         events.append("тело")
    #  19 |         raise ValueError("x")
    #  20 |     events.append("после2")
    #  21 | except ValueError:
    #  22 |     events.append("поймано")
    #  23 | b = len(events)
    #
    # len_first: значение a, число (строка 15)
    # after_count: сколько раз в events встречается "после", число
    # exit_count: сколько раз в events встречается "выход", число
    # len_second: значение b, число (строка 23)
    # last_event: последний элемент events, строка
    # after2_reached: попало ли "после2" в events, True или False

    len_first = None
    after_count = None
    exit_count = None
    len_second = None
    last_event = None
    after2_reached = None

    # Ниже ничего не меняй: это рамка для проверки.
    return len_first, after_count, exit_count, len_second, last_event, after2_reached
