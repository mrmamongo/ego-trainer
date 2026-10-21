from ego.testing import case


@case(
    args=(5,),
    expected='ночь',
    description='5 — последний час ночи',
    level="smoke",
)

@case(
    args=(6,),
    expected='утро',
    description='6 — первый час утра',
    level="smoke",
)

@case(
    args=(12,),
    expected='день',
    description='12 — первый час дня',
    level="smoke",
)

@case(
    args=(18,),
    expected='вечер',
    description='18 — первый час вечера',
    level="smoke",
)

@case(
    args=(0,),
    expected='ночь',
    description='полночь',
    level="full",
)

@case(
    args=(11,),
    expected='утро',
    description='11 — последний час утра',
    level="full",
)

@case(
    args=(17,),
    expected='день',
    description='17 — последний час дня',
    level="full",
)

@case(
    args=(23,),
    expected='вечер',
    description='23 — последний час суток',
    level="full",
)
def task_fn17_part_of_day(hour):
    ...
