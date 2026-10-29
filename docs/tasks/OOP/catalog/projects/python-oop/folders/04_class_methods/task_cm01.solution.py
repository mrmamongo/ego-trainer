def task_cm01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def greet(name):
    #   2 |     return "Привет, " + name
    #   3 | def bye(name):
    #   4 |     return "Пока, " + name
    #   5 | handlers = [greet, bye]
    #   6 | a = handlers[0]("Аня")
    #   7 | b = handlers[1]("Боря")
    #   8 | def make_adder(k):
    #   9 |     def add(x):
    #  10 |         return x + k
    #  11 |     return add
    #  12 | plus5 = make_adder(5)
    #  13 | c = plus5(10)
    #  14 | d = len(handlers)
    #  15 | g = bye
    #  16 | e = g("Вика")
    #  17 | f = g is handlers[1]
    #
    # a_value: что вернул вызов в строке 6 (строка)
    # b_value: что вернул вызов в строке 7 (строка)
    # c_value: что вернул plus5(10) в строке 13
    # d_value: сколько элементов в handlers
    # e_value: что вернул g("Вика") в строке 16 (строка)
    # f_value: указывает ли g на ту же функцию, что handlers[1] (True или False)
    a_value = 'Привет, Аня'
    b_value = 'Пока, Боря'
    c_value = 15
    d_value = 2
    e_value = 'Пока, Вика'
    f_value = True
    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, e_value, f_value
