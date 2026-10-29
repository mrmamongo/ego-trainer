from ego.testing import case, rules

@rules(
    require_classes=['Score'],
    require_decorators={'Score': ['dataclass']},
)
@case(
    args=([['Аня', 50], ['Боря', 70], ['Вика', 60]], 2),
    expected=[['Боря', 70], ['Вика', 60]],
    description='двое лучших',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 50]], 3),
    expected=[['Аня', 50]],
    description='игроков меньше, чем просили',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 5),
    expected=[],
    description='пустая таблица',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Боря', 50], ['Аня', 50], ['Вика', 90]], 3),
    expected=[['Вика', 90], ['Аня', 50], ['Боря', 50]],
    description='равные очки — по имени',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 5], ['Боря', 7]], 0),
    expected=[],
    description='просят ноль мест',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', -3], ['Боря', -10], ['Вика', 0]], 2),
    expected=[['Вика', 0], ['Аня', -3]],
    description='отрицательные очки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_dc13_top_scores(rows, n):
    ...
