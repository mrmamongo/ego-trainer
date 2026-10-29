def task_dc03_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | from dataclasses import dataclass, replace, FrozenInstanceError
    #   2 | @dataclass(frozen=True)
    #   3 | class Profile:
    #   4 |     name: str
    #   5 |     level: int = 1
    #   6 | p = Profile("Аня")
    #   7 | try:
    #   8 |     p.level = 5
    #   9 |     r1 = "изменили"
    #  10 | except FrozenInstanceError:
    #  11 |     r1 = "нельзя"
    #  12 | q = replace(p, level=p.level + 1)
    #  13 | r2 = p.level
    #  14 | r3 = q.level
    #  15 | r4 = p == q
    #  16 | r5 = q == Profile("Аня", 2)
    #  17 | r6 = p is q
    #
    # try_result: значение r1 после блока try/except (строки 7-11)
    # p_level: значение r2 (строка 13)
    # q_level: значение r3 (строка 14)
    # p_eq_q: значение r4 (строка 15, True или False)
    # q_eq_new: значение r5 (строка 16, True или False)
    # p_is_q: значение r6 (строка 17, True или False)

    try_result = 'нельзя'
    p_level = 1
    q_level = 2
    p_eq_q = False
    q_eq_new = True
    p_is_q = False

    # Ниже ничего не меняй: это рамка для проверки.
    return try_result, p_level, q_level, p_eq_q, q_eq_new, p_is_q
