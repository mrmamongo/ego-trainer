from ego.testing import case

@case(
    args=(),
    expected=(2, 2, 2, 2, 10),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_cm03_trace():
    ...
