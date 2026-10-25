def task_er01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | log = ""
    #   2 | try:
    #   3 |     log = log + "a"
    #   4 |     n = int("x7")
    #   5 |     log = log + "b"
    #   6 | except ValueError:
    #   7 |     log = log + "c"
    #   8 | else:
    #   9 |     log = log + "d"
    #  10 | finally:
    #  11 |     log = log + "e"
    #
    # b_ran: выполнилась ли строка 5 (True или False)
    # c_ran: выполнилась ли строка 7 (True или False)
    # d_ran: выполнилась ли строка 9 (True или False)
    # e_ran: выполнилась ли строка 11 (True или False)
    # log_final: значение log после всего блока (строка в кавычках)

    b_ran = False
    c_ran = True
    d_ran = False
    e_ran = True
    log_final = "ace"

    # Ниже ничего не меняй: это рамка для проверки.
    return b_ran, c_ran, d_ran, e_ran, log_final
