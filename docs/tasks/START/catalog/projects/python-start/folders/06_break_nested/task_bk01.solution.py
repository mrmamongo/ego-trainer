def task_bk01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | total = 0
    #   2 | for number in [4, 6, -1, 9]:
    #   3 |     if number < 0:
    #   4 |         break
    #   5 |     total = total + number
    #
    # total_pass_1: total после тела цикла на 1-м проходе
    # total_pass_2: total после тела цикла на 2-м проходе
    # passes_started: сколько проходов цикл начал (прерванный тоже считается)
    # number_final: значение number после завершения цикла
    # total_final: значение total после завершения цикла

    total_pass_1 = 4
    total_pass_2 = 10
    passes_started = 3
    number_final = -1
    total_final = 10

    # Ниже ничего не меняй: это рамка для проверки.
    return total_pass_1, total_pass_2, passes_started, number_final, total_final
