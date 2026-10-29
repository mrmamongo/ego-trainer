from ego.testing import case

@case(
    args=(),
    expected=(150, 10, 15, 16, True),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_pr01_trace():
    ...
