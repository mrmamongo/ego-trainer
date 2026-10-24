from ego.testing import case

@case(
    args=("aaabccdd",),
    expected="a3b1c2d2",
    description="серии разной длины",
    level="smoke",
)

@case(
    args=("abc",),
    expected="a1b1c1",
    description="без повторов",
    level="smoke",
)

@case(
    args=("zzzz",),
    expected="z4",
    description="одна серия",
    level="smoke",
)

@case(
    args=("",),
    expected="",
    description="пустая строка",
    level="full",
)

@case(
    args=("a",),
    expected="a1",
    description="один символ",
    level="full",
)

@case(
    args=("aabbaa",),
    expected="a2b2a2",
    description="повтор буквы после другой",
    level="full",
)

@case(
    args=("aaaaaaaaaaaa",),
    expected="a12",
    description="длина серии из двух цифр",
    level="full",
)

@case(
    args=("abba",),
    expected="a1b2a1",
    description="серия в середине",
    level="full",
)
def task_s17_compress(text):
    ...
