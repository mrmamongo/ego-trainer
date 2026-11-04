from ego.testing import case

@case(
    args=(),
    expected=(False, True, True, False, True),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_mo04_trace():
    ...
