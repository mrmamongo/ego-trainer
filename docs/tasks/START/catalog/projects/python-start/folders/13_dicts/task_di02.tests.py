from ego.testing import case, rules

@rules(
    forbid_nodes=['If', 'IfExp', 'Try'],
    messages={
        'If': 'Здесь нужен метод get со вторым аргументом, ветвление не требуется',
        'IfExp': 'Здесь нужен метод get со вторым аргументом, ветвление не требуется',
        'Try': 'Здесь нужен метод get со вторым аргументом, try не требуется',
    },
)
@case(
    args=({'чай': 50, 'кофе': 120}, 'кофе'),
    expected=120,
    description='товар есть',
    level='smoke',
    check_inputs_unchanged=True,
)
@case(
    args=({'чай': 50}, 'сок'),
    expected=0,
    description='товара нет',
    level='smoke',
    check_inputs_unchanged=True,
)
@case(
    args=({}, 'чай'),
    expected=0,
    description='пустой словарь',
    level='smoke',
    check_inputs_unchanged=True,
)
@case(
    args=({'чай': 50, 'кофе': 120, 'сок': 80}, 'чай'),
    expected=50,
    description='первый из трёх',
    level='full',
    check_inputs_unchanged=True,
)
@case(
    args=({'хлеб': 0}, 'хлеб'),
    expected=0,
    description='цена ровно ноль',
    level='full',
    check_inputs_unchanged=True,
)
@case(
    args=({'чай': 50}, 'Чай'),
    expected=0,
    description='регистр важен: другой ключ',
    level='full',
    check_inputs_unchanged=True,
)
def task_di02_price_of(prices, item):
    ...
