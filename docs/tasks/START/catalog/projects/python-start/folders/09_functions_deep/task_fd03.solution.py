def task_fd03_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def price_with_tax(price, rate=10, bonus=0):
    #   2 |     return price + price * rate // 100 - bonus
    #   3 | a = price_with_tax(200)
    #   4 | b = price_with_tax(200, 20)
    #   5 | c = price_with_tax(200, bonus=15)
    #   6 | d = price_with_tax(rate=50, price=100)
    #
    # a_after_3: значение a после строки 3
    # b_after_4: значение b после строки 4
    # c_after_5: значение c после строки 5
    # d_after_6: значение d после строки 6
    # rate_in_line_5: чему равен rate внутри вызова на строке 5

    a_after_3 = 220
    b_after_4 = 240
    c_after_5 = 205
    d_after_6 = 150
    rate_in_line_5 = 10

    # Ниже ничего не меняй: это рамка для проверки.
    return a_after_3, b_after_4, c_after_5, d_after_6, rate_in_line_5
