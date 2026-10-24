def task_ts04_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | words = ["a", "b", "a", "c", "b", "a"]
    #   2 | unique = set(words)
    #   3 | count_all = len(words)
    #   4 | count_unique = len(unique)
    #   5 | has_c = "c" in unique
    #   6 | has_z = "z" in unique
    #   7 | unique.add("a")
    #   8 | unique.add("z")
    #   9 | count_now = len(unique)
    #
    # count_all: значение count_all после строки 3
    # count_unique: значение count_unique после строки 4
    # has_c: значение has_c после строки 5 (True или False)
    # has_z: значение has_z после строки 6 (True или False)
    # count_now: значение count_now после строки 9

    count_all = 6
    count_unique = 3
    has_c = True
    has_z = False
    count_now = 4

    # Ниже ничего не меняй: это рамка для проверки.
    return count_all, count_unique, has_c, has_z, count_now
