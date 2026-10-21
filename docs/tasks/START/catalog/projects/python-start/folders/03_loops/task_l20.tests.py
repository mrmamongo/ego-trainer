from ego.testing import case

@case(
    args=(['слон', 'кот', 'мышь'],),
    expected='кот',
    description='одно самое короткое',
    level="smoke",
)

@case(
    args=(['a'],),
    expected='a',
    description='одно слово',
    level="smoke",
)

@case(
    args=(['bb', 'a', 'c'],),
    expected='a',
    description='ничья — раньше побеждает',
    level="smoke",
)

@case(
    args=(['dd', 'cc', 'bb'],),
    expected='dd',
    description='все одной длины — первое',
    level="full",
)

@case(
    args=(['один', 'два', 'три'],),
    expected='два',
    description='ничья из двух, раньше "два"',
    level="full",
)

@case(
    args=(['abc', '', 'x'],),
    expected='',
    description='пустая строка самая короткая',
    level="full",
)

@case(
    args=(['abcde', 'abcd'],),
    expected='abcd',
    description='короткое в конце',
    level="full",
)
def task_l20_shortest_word(words):
    ...
