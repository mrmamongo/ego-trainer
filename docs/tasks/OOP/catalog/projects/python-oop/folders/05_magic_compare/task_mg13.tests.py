from ego.testing import case, rules

@rules(
    require_classes=['Version'],
    require_methods={'Version': ['__init__', '__lt__']},
)
@case(
    args=(['1.9', '1.10'],),
    expected={'sorted': ['1.9', '1.10'], 'newest': '1.10'},
    description='десятая версия новее девятой',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['2.0', '10.0', '9.5'],),
    expected={'sorted': ['2.0', '9.5', '10.0'], 'newest': '10.0'},
    description='мажорные версии',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['3.1'],),
    expected={'sorted': ['3.1'], 'newest': '3.1'},
    description='одна версия',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected={'sorted': [], 'newest': None},
    description='пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['1.10.1', '1.9.9', '1.10.0'],),
    expected={'sorted': ['1.9.9', '1.10.0', '1.10.1'], 'newest': '1.10.1'},
    description='три числа',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['1.0', '1.0'],),
    expected={'sorted': ['1.0', '1.0'], 'newest': '1.0'},
    description='одинаковые версии',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['0.99', '1.0', '0.100'],),
    expected={'sorted': ['0.99', '0.100', '1.0'], 'newest': '1.0'},
    description='нули и сотни',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg13_versions(texts):
    ...
