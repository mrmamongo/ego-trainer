from ego.testing import case, rules

@rules(
    forbid_methods=['setdefault'],
    forbid_imports=['collections'],
    messages={
        'setdefault': 'Создавай список при первой встрече ключа сам, без setdefault',
        'collections': 'Модуль collections здесь не нужен: группировку нужно написать самому',
    },
)
@case(
    args=(['кот', 'мышь', 'дом'],),
    expected={3: ['кот', 'дом'], 4: ['мышь']},
    description='две длины',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['а'],),
    expected={1: ['а']},
    description='одно слово',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected={},
    description='пустой список',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['ab', 'cd', 'ef'],),
    expected={2: ['ab', 'cd', 'ef']},
    description='все одной длины',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'bb', 'ccc'],),
    expected={1: ['a'], 2: ['bb'], 3: ['ccc']},
    description='все разные',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['яблоко', 'груша', 'слива', 'киви', 'дыня'],),
    expected={6: ['яблоко'], 5: ['груша', 'слива'], 4: ['киви', 'дыня']},
    description='порядок внутри группы сохраняется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di09_group_by_length(words):
    ...
