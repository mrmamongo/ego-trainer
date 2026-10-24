from ego.testing import case

@case(
    args=('a,b,c',),
    expected='слов: 3',
    description='слова через запятую',
    level="smoke",
)

@case(
    args=('привет мир',),
    expected='слов: 2',
    description='слова через пробел',
    level="smoke",
)

@case(
    args=('один',),
    expected='слов: 1',
    description='одно слово',
    level="smoke",
)

@case(
    args=('',),
    expected='слов: 0',
    description='пустая строка',
    level="full",
)

@case(
    args=(',,',),
    expected='слов: 0',
    description='одни запятые',
    level="full",
)

@case(
    args=(' раз, два,три ',),
    expected='слов: 3',
    description='запятые и пробелы вперемешку',
    level="full",
)

def task_fd17_report(text):
    ...
