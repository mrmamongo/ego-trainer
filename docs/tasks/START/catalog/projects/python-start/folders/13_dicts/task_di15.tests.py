from ego.testing import case

@case(
    args=([{'id': 'q1', 'title': 'Найти ключ'}, {'id': 'q2', 'title': 'Победить дракона'}, {'id': 'q3', 'title': 'Собрать грибы'}], ['q1']),
    expected={'q1': 'done', 'q2': 'open', 'q3': 'open'},
    description='выполнен один квест',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 'q1', 'title': 'Найти ключ'}, {'id': 'q2', 'title': 'Победить дракона'}, {'id': 'q3', 'title': 'Собрать грибы'}], []),
    expected={'q1': 'open', 'q2': 'open', 'q3': 'open'},
    description='ничего не выполнено',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], ['q1']),
    expected={},
    description='нет квестов',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 'q1', 'title': 'Найти ключ'}, {'id': 'q2', 'title': 'Победить дракона'}, {'id': 'q3', 'title': 'Собрать грибы'}], ['q3', 'q1', 'q2']),
    expected={'q1': 'done', 'q2': 'done', 'q3': 'done'},
    description='всё выполнено, порядок done_ids другой',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 'q1', 'title': 'Найти ключ'}, {'id': 'q2', 'title': 'Победить дракона'}, {'id': 'q3', 'title': 'Собрать грибы'}], ['q9']),
    expected={'q1': 'open', 'q2': 'open', 'q3': 'open'},
    description='лишний id в done_ids игнорируется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di15_quest_progress(quests, done_ids):
    ...
