from ego.testing import case

@case(
    args=(['ccc', 'a', 'bb'],),
    expected=['a', 'bb', 'ccc'],
    description='разная длина',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=(['bb', 'a', 'cc', 'd'],),
    expected=['a', 'd', 'bb', 'cc'],
    description='равные длины сохраняют порядок',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=(['кот', 'я', 'слон'],),
    expected=['я', 'кот', 'слон'],
    description='русские слова',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([],),
    expected=[],
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=(['один'],),
    expected=['один'],
    description='одно слово',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=(['xx', 'yy', 'zz'],),
    expected=['xx', 'yy', 'zz'],
    description='все одной длины',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=(['abc', '', 'ab', 'a'],),
    expected=['', 'a', 'ab', 'abc'],
    description='пустая строка',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=(['aa', 'b', 'aa', 'c'],),
    expected=['b', 'c', 'aa', 'aa'],
    description='повторы',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li12_sort_by_length(words):
    ...
