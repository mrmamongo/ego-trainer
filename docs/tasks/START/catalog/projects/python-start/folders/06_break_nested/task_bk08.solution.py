def task_bk08_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | n = 1
    #   2 | steps = 0
    #   3 | while True:
    #   4 |     n = n * 3
    #   5 |     steps = steps + 1
    #   6 |     if n > 50:
    #   7 |         break
    #
    # n_pass_2: n после тела цикла на 2-м проходе
    # n_pass_3: n после тела цикла на 3-м проходе
    # big_at_pass_3: верно ли n > 50 на 3-м проходе (True или False)
    # steps_final: значение steps после цикла
    # n_final: значение n после цикла

    n_pass_2 = 9
    n_pass_3 = 27
    big_at_pass_3 = False
    steps_final = 4
    n_final = 81

    # Ниже ничего не меняй: это рамка для проверки.
    return n_pass_2, n_pass_3, big_at_pass_3, steps_final, n_final
