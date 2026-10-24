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
    args=('да нет да',),
    expected={'да': 2, 'нет': 1},
    description='повтор слова',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('один',),
    expected={'один': 1},
    description='одно слово',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('',),
    expected={},
    description='пустая строка',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('a b c a b a',),
    expected={'a': 3, 'b': 2, 'c': 1},
    description='три слова с разным числом повторов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('кот кот кот',),
    expected={'кот': 3},
    description='одно слово много раз',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('к  о   т',),
    expected={'к': 1, 'о': 1, 'т': 1},
    description='несколько пробелов подряд',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di06_count_words(text):
    ...
