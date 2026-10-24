from ego.testing import case, rules

@case(
    args=(['кот', 'слон', 'мышь'],),
    expected='3 слов, самое длинное: слон',
    description='ничья по длине: первое слово',
    level="smoke",
)

@case(
    args=(['a'],),
    expected='1 слов, самое длинное: a',
    description='одно слово',
    level="smoke",
)

@case(
    args=([],),
    expected='0 слов, самое длинное: -',
    description='пустой список',
    level="smoke",
)

@case(
    args=(['', 'ab', ''],),
    expected='1 слов, самое длинное: ab',
    description='пустые строки не считаются',
    level="full",
)

@case(
    args=([''],),
    expected='0 слов, самое длинное: -',
    description='только пустая строка',
    level="full",
)

@case(
    args=(['a', 'bb', 'cc'],),
    expected='3 слов, самое длинное: bb',
    description='из двух равных берётся первое',
    level="full",
)

@case(
    args=(['ab', 'ab'],),
    expected='2 слов, самое длинное: ab',
    description='одинаковые слова',
    level="full",
)


@rules(forbid_names=["max", "sorted"])

def task_fd20_summary(words):
    ...
