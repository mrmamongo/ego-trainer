from ego.testing import case

@case(
    args=(['add 5', 'sub 2'],),
    expected=(3, 2, 0),
    description='старый сценарий: add и sub',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=(['add 5', 'jump', 'reset'],),
    expected=(0, 2, 1),
    description='старый сценарий: незнакомая команда',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=(['add 5', 'add 3', 'undo'],),
    expected=(5, 3, 0),
    description='undo отменяет последнюю команду',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=(['undo', 'add 1'],),
    expected=(1, 1, 1),
    description='undo без истории игнорируется',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([],),
    expected=(0, 0, 0),
    description='старый сценарий: нет команд',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(['add 4', 'reset', 'add 1'],),
    expected=(1, 3, 0),
    description='старый сценарий: reset',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@case(
    args=(['add 5', 'add 3', 'undo', 'undo'],),
    expected=(0, 4, 0),
    description='два undo подряд',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@case(
    args=(['add 5', 'undo', 'undo'],),
    expected=(0, 2, 1),
    description='undo больше, чем команд',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(['add 9', 'reset', 'undo'],),
    expected=(9, 3, 0),
    description='undo отменяет reset',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@case(
    args=(['fly', 'undo', 'sub 3'],),
    expected=(-3, 1, 2),
    description='игнорируемые команды в историю не попадают',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

def task_rv12_run(commands):
    ...
