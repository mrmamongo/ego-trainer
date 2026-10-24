from ego.testing import case

@case(
    args=({'кино': 300, 'транспорт': 100, 'еда': 300, 'книги': 50}, 2),
    expected=[['еда', 300], ['кино', 300]],
    description='равные суммы идут по алфавиту',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'а': 1, 'б': 5, 'в': 3}, 3),
    expected=[['б', 5], ['в', 3], ['а', 1]],
    description='по убыванию суммы',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({}, 3),
    expected=[],
    description='пустой словарь',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'кино': 300, 'транспорт': 100, 'еда': 300, 'книги': 50}, 0),
    expected=[],
    description='ноль категорий',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'а': 1}, 5),
    expected=[['а', 1]],
    description='n больше числа категорий',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'кино': 300, 'транспорт': 100, 'еда': 300, 'книги': 50}, 4),
    expected=[['еда', 300], ['кино', 300], ['транспорт', 100], ['книги', 50]],
    description='все категории',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di22_top_categories(totals, n):
    ...
