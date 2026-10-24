def task_di01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | menu = {"суп": 200, "салат": 150}
    #   2 | a = menu["суп"]
    #   3 | b = menu.get("пицца", 0)
    #   4 | c = "салат" in menu
    #   5 | menu["пицца"] = 400
    #   6 | d = menu.get("пицца", 0)
    #   7 | menu["суп"] = menu["суп"] + 50
    #   8 | n = len(menu)
    #   9 | e = 200 in menu
    #
    # a_value: значение, которое лежит в menu по ключу "суп" (строка 2)
    # b_value: что вернул get для ключа "пицца" в строке 3
    # c_value: ответ на проверку в строке 4 (True или False)
    # d_value: что вернул get для "пицца" в строке 6
    # soup_final: menu["суп"] после строки 7
    # n_value: сколько пар в menu после строки 7
    # e_value: ответ на проверку в строке 9 (True или False)

    a_value = 200
    b_value = 0
    c_value = True
    d_value = 400
    soup_final = 250
    n_value = 3
    e_value = False

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, soup_final, n_value, e_value
