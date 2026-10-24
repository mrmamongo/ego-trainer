from ego.testing import case

@case(
    args=(),
    expected=(6, 3, True, False, 4),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_ts04_trace():
    ...
