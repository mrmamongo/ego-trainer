from ego.testing import case, rules

@rules(
    require_classes=['Item'],
    require_decorators={'Item': ['dataclass']},
)
@case(
    args=([['Меч', 3], ['Щит', 1]], 'Щит', 1),
    expected=True,
    description='товар с таким количеством есть',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Меч', 3], ['Щит', 1]], 'Щит', 2),
    expected=False,
    description='название есть, количество другое',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 'Меч', 1),
    expected=False,
    description='склад пуст',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Меч', 3]], 'Меч', 3),
    expected=True,
    description='один товар на складе',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Меч', 3], ['Меч', 5]], 'Меч', 5),
    expected=True,
    description='одно название дважды, ищем вторую запись',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Меч', 3]], 'Щит', 3),
    expected=False,
    description='количество то же, название другое',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_dc05_has_item(stock, name, qty):
    ...
