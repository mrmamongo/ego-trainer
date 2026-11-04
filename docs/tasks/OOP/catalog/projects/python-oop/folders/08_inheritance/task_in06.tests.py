from ego.testing import case, rules

@rules(
    require_classes=['Unit', 'Mage'],
    require_bases={'Mage': ['Unit']},
    require_methods={'Unit': ['__init__', 'is_alive'], 'Mage': ['__init__']},
)
@case(
    args=([['new', 'Mage', 'Мерлин', 30, 50], ['get', 'mana'], ['get', 'name']],),
    expected=['ok', 50, 'Мерлин'],
    description='у мага есть имя и мана',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Mage', 'Гэндальф', 80, 100], ['get', 'hp'], ['is_alive']],),
    expected=['ok', 80, True],
    description='здоровье и is_alive',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Unit', 'Тень', 0], ['is_alive']],),
    expected=['ok', False],
    description='обычный юнит не сломан',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Mage', 'Слабый', 0, 5], ['is_alive'], ['is', 'Unit']],),
    expected=['ok', False, True],
    description='маг с нулём hp, он тоже Unit',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Mage', 'Аня', 10, 7], ['set', 'hp', 3], ['get', 'hp'], ['get', 'mana']],),
    expected=['ok', 'ok', 3, 7],
    description='поля меняются независимо',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in06_mage(actions):
    ...
