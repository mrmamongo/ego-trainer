def task_bk10_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | first = "?"
    #   2 | for number in [3, 5, 7]:
    #   3 |     if number % 2 == 0:
    #   4 |         first = "even"
    #   5 |         break
    #   6 | else:
    #   7 |     first = "none"
    #   8 | second = "?"
    #   9 | for number in [3, 6, 7]:
    #  10 |     if number % 2 == 0:
    #  11 |         second = "even"
    #  12 |         break
    #  13 | else:
    #  14 |     second = "none"
    #
    # first_final: значение first после первого цикла
    # number_after_first: значение number сразу после первого цикла
    # second_final: значение second после второго цикла
    # else_ran_second: выполнялся ли else у второго цикла (True или False)
    # number_final: значение number после второго цикла

    first_final = 'none'
    number_after_first = 7
    second_final = 'even'
    else_ran_second = False
    number_final = 6

    # Ниже ничего не меняй: это рамка для проверки.
    return first_final, number_after_first, second_final, else_ran_second, number_final
