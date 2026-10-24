from ego.testing import case, rules

@case(
    args=("banana", "an", "AN"),
    expected="bANANa",
    description="две замены",
    level="smoke",
)

@case(
    args=("a-b-c", "-", "+"),
    expected="a+b+c",
    description="замена одного символа",
    level="smoke",
)

@case(
    args=("hello", "z", "y"),
    expected="hello",
    description="образца нет",
    level="smoke",
)

@case(
    args=("", "a", "b"),
    expected="",
    description="пустой текст",
    level="full",
)

@case(
    args=("aaa", "aa", "b"),
    expected="ba",
    description="без перекрытий",
    level="full",
)

@case(
    args=("abc", "abc", ""),
    expected="",
    description="заменили весь текст пустой строкой",
    level="full",
)

@case(
    args=("abab", "ab", "x"),
    expected="xx",
    description="подряд идущие совпадения",
    level="full",
)

@case(
    args=("aaaa", "a", "aa"),
    expected="aaaaaaaa",
    description="замена длиннее образца",
    level="full",
)

@case(
    args=("a-b-c", "-", ""),
    expected="abc",
    description="удаление символа",
    level="full",
)


@rules(
    forbid_methods=["replace", "split", "join"],
    messages={"replace": "Метод replace() использовать нельзя: заменяй циклом и срезами"},
)

def task_s16_replace_all(text, old, new):
    ...
