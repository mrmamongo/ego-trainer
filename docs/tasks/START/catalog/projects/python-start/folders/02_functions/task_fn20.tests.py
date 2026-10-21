from ego.testing import case


@case(
    args=(20, True, False),
    expected=True,
    description='совершеннолетний с билетом',
    level="smoke",
)

@case(
    args=(20, False, False),
    expected=False,
    description='совершеннолетний без билета',
    level="smoke",
)

@case(
    args=(20, False, True),
    expected=True,
    description='VIP без билета',
    level="smoke",
)

@case(
    args=(17, True, True),
    expected=False,
    description='несовершеннолетний VIP с билетом',
    level="full",
)

@case(
    args=(18, True, False),
    expected=True,
    description='ровно 18 лет, билет есть',
    level="full",
)

@case(
    args=(18, False, False),
    expected=False,
    description='ровно 18 лет, билета нет',
    level="full",
)

@case(
    args=(17, False, True),
    expected=False,
    description='несовершеннолетний VIP',
    level="full",
)

@case(
    args=(30, True, True),
    expected=True,
    description='VIP с билетом',
    level="full",
)
def task_fn20_can_enter(age, has_ticket, is_vip):
    ...
