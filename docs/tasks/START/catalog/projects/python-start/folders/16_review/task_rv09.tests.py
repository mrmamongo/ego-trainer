from ego.testing import case

@case(
    args=({'id': 'q1', 'goal': 5, 'progress': 5, 'reward': 50}, []),
    expected={'status': 'granted', 'coins': 50},
    description='квест выполнен',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'id': 'q1', 'goal': 5, 'progress': 2, 'reward': 50}, []),
    expected={'status': 'rejected', 'reason': 'not_finished'},
    description='квест не закончен',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'id': 'q2', 'goal': 3, 'progress': 3, 'reward': 20}, ['q2']),
    expected={'status': 'rejected', 'reason': 'already_claimed'},
    description='награду уже брали',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'id': 'q3', 'goal': 4, 'progress': 9, 'reward': 10}, ['q1']),
    expected={'status': 'granted', 'coins': 10},
    description='перевыполнен, другие уже взяты',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'id': 'q4', 'goal': 4, 'progress': 3, 'reward': 10}, ['q4']),
    expected={'status': 'rejected', 'reason': 'not_finished'},
    description='не закончен: код раньше, чем already_claimed',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'id': 'q5', 'goal': 1, 'progress': 0, 'reward': 5}, []),
    expected={'status': 'rejected', 'reason': 'not_finished'},
    description='прогресс нулевой',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'id': 'q6', 'goal': 0, 'progress': 0, 'reward': 7}, []),
    expected={'status': 'granted', 'coins': 7},
    description='цель нулевая',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
)

def task_rv09_claim_reward(quest, claimed_ids):
    ...
