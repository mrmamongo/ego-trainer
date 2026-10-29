from ego.testing import case

@case(
    args=(),
    expected=(True, True, 6, False, 0, False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_cl10_trace():
    ...
