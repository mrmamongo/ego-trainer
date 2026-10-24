from ego.testing import case

@case(
    args=({'gold': 10, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': False}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, 'q1'),
    expected=({'gold': 15, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': True}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, True),
    description='награда выдана один раз',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'gold': 15, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': True}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, 'q1'),
    expected=({'gold': 15, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': True}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, False),
    description='повторный вызов: награды нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'gold': 10, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': False}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, 'q2'),
    expected=({'gold': 10, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': False}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, False),
    description='квест не выполнен',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'gold': 10, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': False}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, 'q9'),
    expected=({'gold': 10, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': False}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, False),
    description='неизвестный квест',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'gold': 10, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': False}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, 'q3'),
    expected=({'gold': 10, 'quests': {'q1': {'reward': 5, 'done': True, 'rewarded': False}, 'q2': {'reward': 20, 'done': False, 'rewarded': False}, 'q3': {'reward': 7, 'done': True, 'rewarded': True}}}, False),
    description='награда выдана ранее',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'gold': 0, 'quests': {}}, 'q1'),
    expected=({'gold': 0, 'quests': {}}, False),
    description='пустой журнал квестов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'gold': 3, 'quests': {'z': {'reward': 0, 'done': True, 'rewarded': False}}}, 'z'),
    expected=({'gold': 3, 'quests': {'z': {'reward': 0, 'done': True, 'rewarded': True}}}, True),
    description='нулевая награда тоже выдаётся один раз',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_di26_grant_reward(journal, quest_id):
    ...
