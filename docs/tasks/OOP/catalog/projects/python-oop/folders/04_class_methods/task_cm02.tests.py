from ego.testing import case

@case(
    args=(),
    expected=(12, 2, 2, 5, 0),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_cm02_trace():
    ...
