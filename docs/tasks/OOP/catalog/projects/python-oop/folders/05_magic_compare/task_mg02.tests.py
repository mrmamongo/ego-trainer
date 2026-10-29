from ego.testing import case

@case(
    args=(),
    expected=(True, False, False, False, True, 1),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_mg02_trace():
    ...
