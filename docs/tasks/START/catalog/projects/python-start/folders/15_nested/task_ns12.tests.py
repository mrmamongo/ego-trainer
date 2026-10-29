from ego.testing import case

@case(
    args=({"a": 1, "b": {"c": 2}},),
    expected=2,
    description='словарь в словаре',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([1, [2, [3]]],),
    expected=3,
    description='вложенные списки',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"users": [{"name": "Аня", "tags": ["a", "b"]}, {"name": "Боря", "tags": []}]},),
    expected=4,
    description='список словарей со списками',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=(7,),
    expected=1,
    description='одно значение',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({},),
    expected=0,
    description='пустой словарь',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([[], {}, [[]]],),
    expected=0,
    description='только пустые контейнеры',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"a": None, "b": "", "c": False, "d": 0},),
    expected=4,
    description='None, пустая строка, False и 0 тоже листья',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"a": 1, "b": [2, {"c": None, "d": []}]},),
    expected=3,
    description='смесь из примера',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)

@case(
    args=([{"x": [{"y": [{"z": 1}]}]}, 2],),
    expected=2,
    description='словари и списки вперемешку, глубоко',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)


def task_ns12_count_leaves(data):
    ...
