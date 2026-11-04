def task_pt01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | nums = [10, 20, 30]
    #   2 | it = iter(nums)
    #   3 | a = next(it)
    #   4 | b = next(it)
    #   5 | rest = list(it)
    #   6 | again = list(it)
    #   7 | c = next(it, -1)
    #   8 | same = iter(it) is it
    #   9 | fresh = iter(nums) is iter(nums)
    #
    # first: значение a, число (строка 3)
    # second: значение b, число (строка 4)
    # rest_len: сколько элементов в rest, число (строка 5)
    # again_len: сколько элементов в again, число (строка 6): итератор уже пуст
    # fallback: значение c, число (строка 7)
    # it_is_iter: значение same, True или False (строка 8)
    # lists_fresh: значение fresh, True или False (строка 9): два вызова iter(nums)

    first = 10
    second = 20
    rest_len = 1
    again_len = 0
    fallback = -1
    it_is_iter = True
    lists_fresh = False

    # Ниже ничего не меняй: это рамка для проверки.
    return first, second, rest_len, again_len, fallback, it_is_iter, lists_fresh
