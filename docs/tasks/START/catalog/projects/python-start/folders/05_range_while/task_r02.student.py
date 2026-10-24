def task_r02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | passes_a = 0
    #   2 | last_a = -1
    #   3 | for i in range(2, 11, 3):
    #   4 |     passes_a = passes_a + 1
    #   5 |     last_a = i
    #   6 | passes_b = 0
    #   7 | for j in range(5, 2):
    #   8 |     passes_b = passes_b + 1
    #
    # passes_a_final: сколько раз выполнился первый цикл (строка 4)
    # i_on_iteration_2: чему равно i во время 2-го прохода первого цикла
    # last_a_final: значение last_a после первого цикла
    # passes_b_final: значение passes_b после второго цикла

    passes_a_final = None
    i_on_iteration_2 = None
    last_a_final = None
    passes_b_final = None

    # Ниже ничего не меняй: это рамка для проверки.
    return passes_a_final, i_on_iteration_2, last_a_final, passes_b_final
