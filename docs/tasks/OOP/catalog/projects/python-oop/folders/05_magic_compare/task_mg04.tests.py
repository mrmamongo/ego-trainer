from ego.testing import case

@case(
    args=(),
    expected=(2, True, False, 2, 1, 2),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_mg04_trace():
    ...
