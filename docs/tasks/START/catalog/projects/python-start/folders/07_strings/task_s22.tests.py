from ego.testing import case, rules

@case(
    args=("abc123!",),
    expected=[3, 3, 1],
    description="буквы, цифры, знак",
    level="smoke",
)

@case(
    args=("Привет, мир",),
    expected=[9, 0, 2],
    description="запятая и пробел",
    level="smoke",
)

@case(
    args=("2024",),
    expected=[0, 4, 0],
    description="только цифры",
    level="smoke",
)

@case(
    args=("",),
    expected=[0, 0, 0],
    description="пустая строка",
    level="full",
)

@case(
    args=(" ",),
    expected=[0, 0, 1],
    description="один пробел",
    level="full",
)

@case(
    args=("Python 3.11!",),
    expected=[6, 3, 3],
    description="пробел, точка, восклицательный знак",
    level="full",
)

@case(
    args=("abc",),
    expected=[3, 0, 0],
    description="только буквы",
    level="full",
)


@rules(forbid_names=["sum"], forbid_methods=["count"])

def task_s22_count_char_types(text):
    ...
