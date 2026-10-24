from ego.testing import case, rules

@case(
    args=(386,),
    expected=17,
    description='разные цифры',
    level="smoke",
)

@case(
    args=(100,),
    expected=1,
    description='сотня с нулями',
    level="smoke",
)

@case(
    args=(555,),
    expected=15,
    description='одинаковые цифры',
    level="smoke",
)

@case(
    args=(999,),
    expected=27,
    description='три девятки',
    level="full",
)

@case(
    args=(120,),
    expected=3,
    description='ноль в конце',
    level="full",
)

@case(
    args=(703,),
    expected=10,
    description='ноль в середине',
    level="full",
)


@rules(
    forbid_names=["str", "round"],
    messages={
        "str": "Тексты использовать нельзя: цифры доставай через // и %",
        "round": "round использовать нельзя: сумма цифр — уже целое число",
    },
)

def task_n03_digit_sum3(n):
    ...
