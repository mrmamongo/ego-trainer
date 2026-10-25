from ego.testing import case

@case(
    args=({"name": "Аня", "age": 20, "address": {"city": "Омск", "zip": "644000"}},),
    expected=[],
    description='хороший профиль',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=({"name": " ", "age": 200, "address": {"city": "Омск"}},),
    expected=["address.zip: missing", "age: out_of_range", "name: empty"],
    description='три проблемы сразу, в алфавитном порядке',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({},),
    expected=["address: missing", "age: missing", "name: missing"],
    description='пустой профиль: нет трёх обязательных полей',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=({"name": "Аня", "age": 20, "address": "Омск"},),
    expected=["address: wrong_type"],
    description='адрес не словарь: внутрь не заходим',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"name": 5, "age": "20", "address": {"city": 1, "zip": 644000}},),
    expected=["address.city: wrong_type", "address.zip: wrong_type", "age: wrong_type", "name: wrong_type"],
    description='неверные типы везде',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"name": "Аня", "age": True, "address": {"city": "Омск", "zip": "64400"}},),
    expected=["address.zip: bad_format", "age: wrong_type"],
    description='bool не число; индекс из 5 цифр',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"name": "Аня", "age": 0, "address": {"city": " ", "zip": "64400a"}, "email": "anya"},),
    expected=["address.city: empty", "address.zip: bad_format", "email: bad_format"],
    description='age=0 допустим; пустой город; плохой индекс и почта',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"name": "Аня", "age": 150, "address": {"city": "Омск", "zip": "644000"}, "email": "a@b.ru"},),
    expected=[],
    description='граница 150 и корректная почта',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=({"name": "Аня", "age": -1, "address": {"city": "Омск", "zip": "644000"}, "email": 7},),
    expected=["age: out_of_range", "email: wrong_type"],
    description='возраст -1; почта не строка',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)
def task_er18_validate_profile(profile):
    ...
