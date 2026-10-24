from ego.testing import case

@case(
    args=('Hello, hello! World.',),
    expected=2,
    description='регистр и знаки не мешают',
    level='smoke',
)

@case(
    args=('a a a',),
    expected=1,
    description='одно слово трижды',
    level='smoke',
)

@case(
    args=('one two three',),
    expected=3,
    description='все слова разные',
    level='smoke',
)

@case(
    args=('',),
    expected=0,
    description='пустая строка',
    level='full',
)

@case(
    args=('Да? Нет! да, нет.',),
    expected=2,
    description='кириллица, вопросы и запятые',
    level='full',
)

@case(
    args=('The cat. The dog!',),
    expected=3,
    description='повтор the при разных знаках',
    level='full',
)

@case(
    args=('Word',),
    expected=1,
    description='одно слово',
    level='full',
)
def task_ts10_count_unique_words(text):
    ...
