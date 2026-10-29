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
    calls_total = None
    # stack_max: сколько вызовов одновременно не закончены в самый глубокий момент.
    stack_max = None
    # inner_result: что вернёт total([3]).
    inner_result = None
    # middle_result: что вернёт total([2, [3]]).
    middle_result = None
    # outer_result_after_item_1: result внешнего вызова после первого элемента (1).
    outer_result_after_item_1 = None
    # answer: итог всей строки 8.
    answer = None

    # Ниже ничего не меняй: это рамка для проверки.
    return calls_total, stack_max, inner_result, middle_result, outer_result_after_item_1, answer
