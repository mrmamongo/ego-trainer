def task_cm02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def double_and_log(func):
    #   2 |     def wrapper(x):
    #   3 |         wrapper.log.append(x)
    #   4 |         return func(x) * 2
    #   5 |     wrapper.log = []
    #   6 |     return wrapper
    #   7 | @double_and_log
    #   8 | def inc(n):
    #   9 |     return n + 1
    #  10 | a = inc(5)
    #  11 | b = inc(0)
    #  12 | c = len(inc.log)
    #  13 | d = inc.log[0]
    #  14 | e = inc.log[-1]
    #
    # a_value: что вернул inc(5) в строке 10
    # b_value: что вернул inc(0) в строке 11
    # c_value: сколько элементов в inc.log после строки 11
    # d_value: первый элемент inc.log
    # e_value: последний элемент inc.log
    a_value = None
    b_value = None
    c_value = None
    d_value = None
    e_value = None
    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, e_value
