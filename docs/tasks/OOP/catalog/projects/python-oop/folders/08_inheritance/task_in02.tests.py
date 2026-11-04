from ego.testing import case

@case(
    args=(),
    expected=(30, 'Мерлин:30/50', 'лучник Робин', 25, 80),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_in02_super():
    ...
