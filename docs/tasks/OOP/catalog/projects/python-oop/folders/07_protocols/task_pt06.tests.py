from ego.testing import case, rules

@rules(
    require_functions=['leaderboard_pages'],
)
@case(
    args=(['a', 'b', 'c'], 2),
    expected=[['a', 'b'], ['c']],
    description='три имени по две на страницу',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'b'], 5),
    expected=[['a', 'b']],
    description='всё помещается на одну страницу',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'b', 'c', 'd'], 2),
    expected=[['a', 'b'], ['c', 'd']],
    description='две полные страницы',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 3),
    expected=[],
    description='пустая таблица',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a'], 1),
    expected=[['a']],
    description='одно имя',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'b', 'c', 'd', 'e', 'f', 'g'], 3),
    expected=[['a', 'b', 'c'], ['d', 'e', 'f'], ['g']],
    description='последняя страница неполная',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt06_pages(names, size):
    ...
