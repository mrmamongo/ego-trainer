from ego.testing import case

@case(
    args=(['кот', 'слон', 'мышь'], 4),
    expected=2,
    description='два слова из трёх подходят',
    level="smoke",
)

@case(
    args=(['a', 'bb', 'ccc'], 2),
    expected=2,
    description='граница включается',
    level="smoke",
)

@case(
    args=(['дом', 'лес'], 5),
    expected=0,
    description='длинных слов нет',
    level="smoke",
)

@case(
    args=([], 3),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=(['abc', 'abcd'], 3),
    expected=2,
    description='все не короче порога',
    level="full",
)

@case(
    args=(['', 'x'], 0),
    expected=2,
    description='порог 0 — подходят все',
    level="full",
)

@case(
    args=(['один', 'два'], 1),
    expected=2,
    description='порог 1',
    level="full",
)
def task_l09_count_long_words(words, min_len):
    ...
