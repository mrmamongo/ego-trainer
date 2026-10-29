from ego.testing import case

@case(
    args=(),
    expected=(10, True, False, False, True),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_cl05_trace():
    ...
