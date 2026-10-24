from ego.testing import case, rules

@case(
    args=('Привет, привет! Мир.',),
    expected=2,
    description='повтор с разным регистром и знаками',
    level="smoke",
)

@case(
    args=('a b c',),
    expected=3,
    description='все слова разные',
    level="smoke",
)

@case(
    args=('Да да ДА',),
    expected=1,
    description='одно слово в разных регистрах',
    level="smoke",
)

@case(
    args=('',),
    expected=0,
    description='пустой текст',
    level="full",
)

@case(
    args=('!!! ... ?',),
    expected=0,
    description='одни знаки препинания',
    level="full",
)

@case(
    args=('Кот, кот. Пёс! кот?',),
    expected=2,
    description='кот и пёс',
    level="full",
)

@case(
    args=('один',),
    expected=1,
    description='одно слово',
    level="full",
)

@case(
    args=('  много   пробелов  ',),
    expected=2,
    description='лишние пробелы',
    level="full",
)

@case(
    args=('Hello, world! hello.',),
    expected=2,
    description='английские слова',
    level="full",
)


@rules(
    forbid_names=["set"],
    messages={"set": "Множества использовать нельзя: храни увиденные слова в списке"},
)

def task_fd13_count_unique_words(text):
    ...
