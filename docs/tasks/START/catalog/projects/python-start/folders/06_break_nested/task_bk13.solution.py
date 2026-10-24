def task_bk13_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | count = 0
    #   2 | for i in [1, 2, 3]:
    #   3 |     for j in [10, 20]:
    #   4 |         count = count + 1
    #   5 |         if i + j == 12:
    #   6 |             break
    #
    # i_at_run_4: чему равно i при 4-м выполнении строки 4 (count = count + 1)
    # j_at_run_4: чему равно j при 4-м выполнении строки 4
    # runs_with_i2: сколько раз выполнилась строка 4, пока i было равно 2
    # count_final: значение count после обоих циклов
    # j_final: значение j после обоих циклов

    i_at_run_4 = 3
    j_at_run_4 = 10
    runs_with_i2 = 1
    count_final = 5
    j_final = 20

    # Ниже ничего не меняй: это рамка для проверки.
    return i_at_run_4, j_at_run_4, runs_with_i2, count_final, j_final
