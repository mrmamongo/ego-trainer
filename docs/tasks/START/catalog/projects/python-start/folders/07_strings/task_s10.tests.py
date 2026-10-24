from ego.testing import case

@case(
    args=("level",),
    expected=True,
    description="простой палиндром",
    level="smoke",
)

@case(
    args=("hello",),
    expected=False,
    description="не палиндром",
    level="smoke",
)

@case(
    args=("Race car",),
    expected=True,
    description="регистр и пробел",
    level="smoke",
)

@case(
    args=("",),
    expected=True,
    description="пустая строка",
    level="full",
)

@case(
    args=("a",),
    expected=True,
    description="один символ",
    level="full",
)

@case(
    args=("ab",),
    expected=False,
    description="два разных",
    level="full",
)

@case(
    args=("А роза упала на лапу Азора",),
    expected=True,
    description="фраза с пробелами",
    level="full",
)

@case(
    args=("Never odd or even",),
    expected=True,
    description="английская фраза",
    level="full",
)

@case(
    args=("не палиндром",),
    expected=False,
    description="фраза, которая не читается наоборот",
    level="full",
)
def task_s10_is_palindrome(text):
    ...
