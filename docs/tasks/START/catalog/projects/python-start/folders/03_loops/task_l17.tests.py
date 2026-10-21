from ego.testing import case

@case(
    args=(['кот', 'слон', 'жираф'], 4),
    expected='слон',
    description='первое из двух подходящих',
    level="smoke",
)

@case(
    args=(['a', 'bb', 'ccc'], 2),
    expected='bb',
    description='граница включается',
    level="smoke",
)

@case(
    args=(['дом', 'лес'], 10),
    expected='',
    description='подходящих нет',
    level="smoke",
)

@case(
    args=([], 3),
    expected='',
    description='пустой список',
    level="full",
)

@case(
    args=(['abcd'], 4),
    expected='abcd',
    description='единственное слово',
    level="full",
)

@case(
    args=(['aaaa', 'bbbbb'], 3),
    expected='aaaa',
    description='первое, а не самое длинное',
    level="full",
)

@case(
    args=(['', 'x'], 1),
    expected='x',
    description='пустая строка не подходит',
    level="full",
)
def task_l17_first_long_word(words, min_len):
    ...
