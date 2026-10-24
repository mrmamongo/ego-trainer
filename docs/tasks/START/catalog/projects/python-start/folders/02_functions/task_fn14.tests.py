from ego.testing import case, rules


@case(
    args=(10, 5),
    expected=2,
    description='делится ровно',
    level="smoke",
)

@case(
    args=(11, 5),
    expected=3,
    description='остаток — нужна ещё одна упаковка',
    level="smoke",
)

@case(
    args=(0, 5),
    expected=0,
    description='предметов нет',
    level="smoke",
)

@case(
    args=(1, 10),
    expected=1,
    description='один предмет — одна упаковка',
    level="full",
)

@case(
    args=(7, 1),
    expected=7,
    description='по одному в упаковке',
    level="full",
)

@case(
    args=(100, 7),
    expected=15,
    description='14 полных и остаток 2',
    level="full",
)

@case(
    args=(6, 6),
    expected=1,
    description='ровно одна упаковка',
    level="full",
)


@rules(
    forbid_imports=["math"],
    messages={"math": "Модуль math использовать нельзя: решай через //, % и if"},
)

def task_fn14_packs(items, per_pack):
    ...
