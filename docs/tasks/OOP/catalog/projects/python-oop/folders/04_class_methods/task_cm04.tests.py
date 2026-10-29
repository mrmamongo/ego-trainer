from ego.testing import case

@case(
    args=(),
    expected=(10, 26, 2, False, 2),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_cm04_trace():
    ...
