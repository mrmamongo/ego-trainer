from ego.testing import case, rules

@rules(
    require_classes=['Item'],
    require_methods={'Item': ['__init__', 'from_dict']},
    require_decorators={'Item.from_dict': ['classmethod']},
)
@case(
    args=({'name': 'Меч', 'price': 120},),
    expected=['Меч', 120],
    description='обычный предмет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'price': 5, 'name': 'Зелье'},),
    expected=['Зелье', 5],
    description='порядок ключей не важен',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'name': 'Щит', 'price': 0},),
    expected=['Щит', 0],
    description='нулевая цена',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'name': 'Лук', 'price': 40, 'count': 3},),
    expected=['Лук', 40],
    description='лишний ключ игнорируется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'name': '', 'price': 1},),
    expected=['', 1],
    description='пустое имя',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm09_item(data):
    ...
