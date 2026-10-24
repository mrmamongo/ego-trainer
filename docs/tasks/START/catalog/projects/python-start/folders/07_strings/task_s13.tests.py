from ego.testing import case

@case(
    args=("кот пёс слон",),
    expected="слон",
    description="самое длинное в конце",
    level="smoke",
)

@case(
    args=("a bb ccc dd eee",),
    expected="ccc",
    description="ничья: первое из равных",
    level="smoke",
)

@case(
    args=("программа",),
    expected="программа",
    description="одно слово",
    level="smoke",
)

@case(
    args=("",),
    expected="",
    description="пустая строка",
    level="full",
)

@case(
    args=("   ",),
    expected="",
    description="только пробелы",
    level="full",
)

@case(
    args=("  один   три ",),
    expected="один",
    description="лишние пробелы",
    level="full",
)

@case(
    args=("аа бб вв",),
    expected="аа",
    description="все одинаковой длины",
    level="full",
)
def task_s13_longest_word(text):
    ...
