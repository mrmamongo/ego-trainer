from ego.testing import case

@case(
    args=(),
    expected=(12, 12, 0, True, 5, 'TypeError'),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_mo03_trace():
    ...
