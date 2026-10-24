from ego.testing import case, rules

@rules(
    forbid_names=['Counter'],
    forbid_methods=['count'],
    forbid_imports=['collections'],
    messages={
        'Counter': 'Счётчик нужно написать самому, без Counter',
        'count': 'Метод count считает за один раз; здесь нужен словарь-счётчик',
        'collections': 'Модуль collections здесь не нужен: счётчик нужно написать самому',
    },
)
@case(
    args=('банан',),
    expected={'б': 1, 'а': 2, 'н': 2},
    description='повторяющиеся буквы',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('ааа',),
    expected={'а': 3},
    description='одна буква',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('',),
    expected={},
    description='пустое слово',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('abc',),
    expected={'a': 1, 'b': 1, 'c': 1},
    description='все разные',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('абба',),
    expected={'а': 2, 'б': 2},
    description='палиндром',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('м',),
    expected={'м': 1},
    description='одна буква в слове',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di07_letter_freq(word):
    ...
