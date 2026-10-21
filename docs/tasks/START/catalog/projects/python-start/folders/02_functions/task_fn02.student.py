def task_fn02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def with_fee(amount):
    #   2 |     fee = amount // 10
    #   3 |     return amount + fee
    #   4 | total = 200
    #   5 | x = with_fee(total)
    #   6 | y = with_fee(50)
    #
    # Впиши вместо None значения ПОСЛЕ строки 6 (в самом конце).
    # fee_exists_outside: True или False. Существует ли переменная fee снаружи функции,
    # то есть сработала бы строка `z = fee` без ошибки?

    x_final = None
    y_final = None
    total_final = None
    fee_exists_outside = None

    # Ниже ничего не меняй: это рамка для проверки.
    return x_final, y_final, total_final, fee_exists_outside
