from ego.testing import case

@case(
    args=('abcdefgh',),
    expected=True,
    description='ровно восемь',
    level="smoke",
)

@case(
    args=('abcdefg',),
    expected=False,
    description='на один короче',
    level="smoke",
)

@case(
    args=('',),
    expected=False,
    description='пустой пароль',
    level="smoke",
)

@case(
    args=('abc', 3),
    expected=True,
    description='свой минимум, граница',
    level="full",
)

@case(
    args=('abc', 4),
    expected=False,
    description='свой минимум, не хватает',
    level="full",
)

@case(
    args=('abcdefghijkl', 12),
    expected=True,
    description='двенадцать',
    level="full",
)

@case(
    args=('', 0),
    expected=True,
    description='нулевой минимум',
    level="full",
)

@case(
    args=('aaaaaaaaaaaaaaaaaaaa',),
    expected=True,
    description='очень длинный',
    level="full",
)

def task_mp11_check_length(pw, min_len=8):
    ...
