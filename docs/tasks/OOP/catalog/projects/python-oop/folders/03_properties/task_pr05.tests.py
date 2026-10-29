from ego.testing import case

@case(
    args=(),
    expected=(50, 0, 99, 10, 50),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_pr05_trace():
    ...
