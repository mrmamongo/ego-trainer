def task_ns01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def total(x):
    #   2 |     if type(x) is not list:
    #   3 |         return x
    #   4 |     result = 0
    #   5 |     for item in x:
    #   6 |         result = result + total(item)
    #   7 |     return result
    #   8 | answer = total([1, [2, [3]]])
    #
    # Впиши вместо None, что получится.

    # calls_total: сколько раз всего вызывалась total, считая первый вызов.
    calls_total = 6
    # stack_max: сколько вызовов одновременно не закончены в самый глубокий момент.
    stack_max = 4
    # inner_result: что вернёт total([3]).
    inner_result = 3
    # middle_result: что вернёт total([2, [3]]).
    middle_result = 5
    # outer_result_after_item_1: result внешнего вызова после первого элемента (1).
    outer_result_after_item_1 = 1
    # answer: итог всей строки 8.
    answer = 6

    # Ниже ничего не меняй: это рамка для проверки.
    return calls_total, stack_max, inner_result, middle_result, outer_result_after_item_1, answer
