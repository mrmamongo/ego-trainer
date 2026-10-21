from ego.testing import case


@case(
    args=('Москва',),
    expected=1,
    description='Москва — 1 день',
    level="smoke",
)

@case(
    args=('Казань',),
    expected=3,
    description='Казань — 3 дня',
    level="smoke",
)

@case(
    args=('Омск',),
    expected=7,
    description='другой город — 7 дней',
    level="smoke",
)

@case(
    args=('Тверь',),
    expected=7,
    description='ещё один другой город',
    level="full",
)

@case(
    args=('',),
    expected=7,
    description='пустое название — тоже «другой город»',
    level="full",
)
def task_fn07_delivery_days(city):
    ...
