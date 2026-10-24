def task_bk02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | total = 0
    #   2 | for number in [4, -6, 5, -1, 3]:
    #   3 |     if number < 0:
    #   4 |         continue
    #   5 |     total = total + number
    #
    # total_pass_2: total после тела цикла на 2-м проходе
    # total_pass_3: total после тела цикла на 3-м проходе
    # passes_started: сколько проходов цикл начал
    # skipped: сколько раз сработал continue
    # total_final: значение total после завершения цикла

    total_pass_2 = 4
    total_pass_3 = 9
    passes_started = 5
    skipped = 2
    total_final = 12

    # Ниже ничего не меняй: это рамка для проверки.
    return total_pass_2, total_pass_3, passes_started, skipped, total_final
