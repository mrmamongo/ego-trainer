from ego.testing import case, rules

@case(
    args=("1234567812345678",),
    expected="************5678",
    description="обычный номер",
    level="smoke",
)

@case(
    args=("12345",),
    expected="*2345",
    description="пять цифр",
    level="smoke",
)

@case(
    args=("123456",),
    expected="**3456",
    description="шесть цифр",
    level="smoke",
)

@case(
    args=("1234",),
    expected="1234",
    description="ровно четыре",
    level="full",
)

@case(
    args=("123",),
    expected="123",
    description="короче четырёх",
    level="full",
)

@case(
    args=("",),
    expected="",
    description="пустая строка",
    level="full",
)


@rules(forbid_methods=["replace"])

def task_s14_mask_card(number):
    ...
