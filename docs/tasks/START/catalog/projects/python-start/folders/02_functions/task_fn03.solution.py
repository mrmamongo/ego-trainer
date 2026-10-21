def task_fn03_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def grade(score):
    #   2 |     if score >= 90:
    #   3 |         return "A"
    #   4 |     if score >= 60:
    #   5 |         return "B"
    #   6 |     return "C"
    #
    # Впиши вместо None, что вернёт grade(...) с указанным баллом (текст в кавычках).
    # Важно: для 95 верны ОБА условия, но return срабатывает один раз.

    grade_95 = 'A'
    grade_90 = 'A'
    grade_60 = 'B'
    grade_59 = 'C'

    # Ниже ничего не меняй: это рамка для проверки.
    return grade_95, grade_90, grade_60, grade_59
