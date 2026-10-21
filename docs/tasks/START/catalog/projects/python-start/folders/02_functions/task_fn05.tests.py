from ego.testing import case


@case(
    args=(6,),
    expected=0,
    description='6 лет — бесплатно',
    level="smoke",
)

@case(
    args=(7,),
    expected=150,
    description='7 лет — граница детского билета',
    level="smoke",
)

@case(
    args=(18,),
    expected=300,
    description='18 лет — взрослый билет',
    level="smoke",
)

@case(
    args=(17,),
    expected=150,
    description='17 лет — ещё детский',
    level="full",
)

@case(
    args=(0,),
    expected=0,
    description='новорождённый',
    level="full",
)

@case(
    args=(40,),
    expected=300,
    description='взрослый',
    level="full",
)
def task_fn05_ticket_price(age):
    ...
