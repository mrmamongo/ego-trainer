from ego.testing import case

@case(
    args=(),
    expected=(10, 20, 1, 0, -1, True, False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_pt01_trace():
    ...
