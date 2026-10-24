def task_di24_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | stock = {"яблоки": 5, "груши": 2, "сливы": 9, "киви": 2}
    #   2 | asc = sorted(stock.items(), key=lambda kv: kv[1])
    #   3 | a = asc[0][0]
    #   4 | b = asc[1][0]
    #   5 | c = asc[3][0]
    #   6 | desc = sorted(stock.items(), key=lambda kv: kv[1], reverse=True)
    #   7 | d = desc[0][0]
    #   8 | e = desc[3][0]
    #   9 | names = sorted(stock)
    #  10 | f = names[-1]
    #
    # first_name: значение a
    # second_name: значение b (два одинаковых значения: подумай про равные значения)
    # last_name: значение c
    # top_name: значение d
    # tail_name: значение e (в списке desc элементы с равным значением остаются в исходном порядке)
    # alpha_last: значение f (последний ключ по алфавиту)

    first_name = 'груши'
    second_name = 'киви'
    last_name = 'сливы'
    top_name = 'сливы'
    tail_name = 'киви'
    alpha_last = 'яблоки'

    # Ниже ничего не меняй: это рамка для проверки.
    return first_name, second_name, last_name, top_name, tail_name, alpha_last
