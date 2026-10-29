from ego.testing import case

@case(
    args=(),
    expected=(212.0, 0, 32.0, -40.0, True),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_pr02_trace():
    ...
