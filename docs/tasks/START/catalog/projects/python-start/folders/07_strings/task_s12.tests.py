from ego.testing import case

@case(
    args=("раз два три",),
    expected=3,
    description="три слова",
    level="smoke",
)

@case(
    args=("один",),
    expected=1,
    description="одно слово",
    level="smoke",
)

@case(
    args=("a  b   c",),
    expected=3,
    description="несколько пробелов подряд",
    level="smoke",
)

@case(
    args=("",),
    expected=0,
    description="пустая строка",
    level="full",
)

@case(
    args=("   ",),
    expected=0,
    description="только пробелы",
    level="full",
)

@case(
    args=("  раз   два  ",),
    expected=2,
    description="пробелы по краям",
    level="full",
)
def task_s12_count_words(text):
    ...
