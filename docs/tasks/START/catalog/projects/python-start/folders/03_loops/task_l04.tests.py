from ego.testing import case, rules

@case(
    args=(['кот', 'пёс'],),
    expected=6,
    description='два слова по три буквы',
    level="smoke",
)

@case(
    args=(['python'],),
    expected=6,
    description='одно слово',
    level="smoke",
)

@case(
    args=([],),
    expected=0,
    description='нет слов — нет букв',
    level="smoke",
)

@case(
    args=(['', 'a', 'bb'],),
    expected=3,
    description='пустая строка добавляет ноль',
    level="full",
)

@case(
    args=(['a b'],),
    expected=3,
    description='пробел тоже символ',
    level="full",
)

@case(
    args=(['один', 'два', 'три'],),
    expected=10,
    description='три слова',
    level="full",
)


@rules(forbid_names=["sum"])

def task_l04_total_length(words):
    ...
