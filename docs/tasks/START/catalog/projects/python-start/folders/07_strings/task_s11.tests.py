from ego.testing import case

@case(
    args=("Иван Петров",),
    expected="И.П.",
    description="имя и фамилия",
    level="smoke",
)

@case(
    args=("Анна Мария Ли",),
    expected="А.М.Л.",
    description="три слова",
    level="smoke",
)

@case(
    args=("Ольга",),
    expected="О.",
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
    args=("  Иван   Петров ",),
    expected="И.П.",
    description="лишние пробелы",
    level="full",
)

@case(
    args=("   ",),
    expected="",
    description="только пробелы",
    level="full",
)
def task_s11_initials(full_name):
    ...
