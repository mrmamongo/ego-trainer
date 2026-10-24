def task_bk03_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | a = 0
    #   2 | for number in [3, 8, 2, 9]:
    #   3 |     if number > 5:
    #   4 |         break
    #   5 |     a = a + number
    #   6 | b = 0
    #   7 | for number in [3, 8, 2, 9]:
    #   8 |     if number > 5:
    #   9 |         continue
    #  10 |     b = b + number
    #
    # a_final: значение a после первого цикла (со словом break)
    # a_passes: сколько проходов начал первый цикл
    # b_final: значение b после второго цикла (со словом continue)
    # b_passes: сколько проходов начал второй цикл
    # number_final: значение number после обоих циклов

    a_final = 3
    a_passes = 2
    b_final = 5
    b_passes = 4
    number_final = 9

    # Ниже ничего не меняй: это рамка для проверки.
    return a_final, a_passes, b_final, b_passes, number_final
