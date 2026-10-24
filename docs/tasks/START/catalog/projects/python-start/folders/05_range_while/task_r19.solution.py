def task_r19_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | x = 100
    #   2 | count = 0
    #   3 | while x > 10:
    #   4 |     x = x - 30
    #   5 |     count = count + 1
    #
    # x_after_iter_1: x после тела на 1-м проходе
    # x_after_iter_2: x после тела на 2-м проходе
    # x_after_iter_3: x после тела на 3-м проходе
    # count_final: значение count после цикла
    # condition_checks_total: сколько раз всего проверялось условие x > 10, считая последнюю проверку, после которой цикл остановился

    x_after_iter_1 = 70
    x_after_iter_2 = 40
    x_after_iter_3 = 10
    count_final = 3
    condition_checks_total = 4

    # Ниже ничего не меняй: это рамка для проверки.
    return x_after_iter_1, x_after_iter_2, x_after_iter_3, count_final, condition_checks_total
