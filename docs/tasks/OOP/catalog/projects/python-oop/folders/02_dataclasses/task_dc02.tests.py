from ego.testing import case

@case(
    args=(),
    expected=(10, 50, 1, 0, False, True),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_dc02_trace():
    ...
