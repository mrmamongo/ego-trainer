def task_dc01_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | from dataclasses import dataclass
    #   2 | @dataclass
    #   3 | class Item:
    #   4 |     name: str
    #   5 |     qty: int
    #   6 | a = Item("Меч", 3)
    #   7 | b = Item("Меч", 3)
    #   8 | c = a
    #   9 | r1 = a == b
    #  10 | r2 = a is b
    #  11 | c.qty = 10
    #  12 | r3 = a.qty
    #  13 | r4 = b.qty
    #  14 | r5 = a == b
    #  15 | r6 = repr(b)
    #
    # eq_before: значение r1, равны ли a и b по полям (строка 9, True или False)
    # same_object: значение r2, один ли это объект (строка 10, True или False)
    # a_qty: значение r3 (строка 12)
    # b_qty: значение r4 (строка 13)
    # eq_after: значение r5 (строка 14, True или False)
    # b_text: значение r6, строка вида Item(...) (строка 15)

    eq_before = None
    same_object = None
    a_qty = None
    b_qty = None
    eq_after = None
    b_text = None

    # Ниже ничего не меняй: это рамка для проверки.
    return eq_before, same_object, a_qty, b_qty, eq_after, b_text
