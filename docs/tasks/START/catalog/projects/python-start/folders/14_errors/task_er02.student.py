def task_er02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | total_a = 0
    #   2 | for text in ["4", "x", "6"]:
    #   3 |     try:
    #   4 |         total_a = total_a + int(text)
    #   5 |     except ValueError:
    #   6 |         total_a = total_a + 100
    #   7 | total_b = 0
    #   8 | try:
    #   9 |     for text in ["4", "x", "6"]:
    #  10 |         total_b = total_b + int(text)
    #  11 | except ValueError:
    #  12 |     total_b = total_b + 100
    #
    # total_a_iter_2: значение total_a после 2-го прохода первого цикла
    # total_a_final: значение total_a после всего первого цикла
    # total_b_final: значение total_b после строки 12
    # last_text: значение text после второго цикла (строка в кавычках)

    total_a_iter_2 = None
    total_a_final = None
    total_b_final = None
    last_text = None

    # Ниже ничего не меняй: это рамка для проверки.
    return total_a_iter_2, total_a_final, total_b_final, last_text
