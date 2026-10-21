def task_fn06_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def discount(price, percent):
    #   2 |     return price - price * percent // 100
    #   3 | a = discount(200, 10)
    #   4 | b = discount(10, 200)
    #   5 | p = 50
    #   6 | c = discount(p, p)
    #
    # Впиши вместо None значение переменной ПОСЛЕ строки 6 (в самом конце).
    # Умножение и `//` считаются слева направо: price * percent, потом // 100.

    a = 180
    b = -10
    c = 25

    # Ниже ничего не меняй: это рамка для проверки.
    return a, b, c
