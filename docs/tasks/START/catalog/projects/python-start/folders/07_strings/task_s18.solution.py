def task_s18_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | raw = "  red green  blue "
    #   2 | clean = raw.strip()
    #   3 | parts = clean.split()
    #   4 | n_parts = len(parts)
    #   5 | joined = "-".join(parts)
    #   6 | pos = clean.find("green")
    #   7 | missing = clean.find("x")
    #   8 | ends = clean.endswith("blue")
    #
    # clean_final .. ends_final: значения clean, n_parts, joined, pos, missing, ends после выполнения кода.
    # Подсказка: find возвращает индекс первого вхождения или -1, если такого нет.

    clean_final = "red green  blue"
    n_parts_final = 3
    joined_final = "red-green-blue"
    pos_final = 4
    missing_final = -1
    ends_final = True

    # Ниже ничего не меняй: это рамка для проверки.
    return clean_final, n_parts_final, joined_final, pos_final, missing_final, ends_final
