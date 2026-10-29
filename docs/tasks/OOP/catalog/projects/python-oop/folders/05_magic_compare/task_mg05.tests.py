from ego.testing import case, rules

@rules(
    require_classes=['Card'],
    require_methods={'Card': ['__init__', '__repr__']},
)
@case(
    args=([['Q', 'червы'], ['10', 'пики']],),
    expected={'one': ["Card('Q', 'червы')", "Card('10', 'пики')"], 'in_list': "[Card('Q', 'червы'), Card('10', 'пики')]"},
    description='две карты',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['A', 'трефы']],),
    expected={'one': ["Card('A', 'трефы')"], 'in_list': "[Card('A', 'трефы')]"},
    description='одна карта',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['K', 'пики'], ['K', 'червы'], ['7', 'бубны']],),
    expected={'one': ["Card('K', 'пики')", "Card('K', 'червы')", "Card('7', 'бубны')"], 'in_list': "[Card('K', 'пики'), Card('K', 'червы'), Card('7', 'бубны')]"},
    description='три карты',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected={'one': [], 'in_list': '[]'},
    description='пустой список карт',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['J', 'бубны'], ['J', 'бубны']],),
    expected={'one': ["Card('J', 'бубны')", "Card('J', 'бубны')"], 'in_list': "[Card('J', 'бубны'), Card('J', 'бубны')]"},
    description='две одинаковые карты',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['2', 'трефы']],),
    expected={'one': ["Card('2', 'трефы')"], 'in_list': "[Card('2', 'трефы')]"},
    description='число в ранге',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg05_show(rows):
    ...
