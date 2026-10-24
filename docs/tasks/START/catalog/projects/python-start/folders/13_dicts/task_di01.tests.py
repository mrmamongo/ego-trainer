from ego.testing import case

@case(
    args=(),
    expected=(200, 0, True, 400, 250, 3, False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_di01_trace():
    ...
