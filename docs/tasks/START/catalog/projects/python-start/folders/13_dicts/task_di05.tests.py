from ego.testing import case

@case(
    args=(),
    expected=(4, 4, 9, 9, 'Миша', 'Паша'),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_di05_trace():
    ...
