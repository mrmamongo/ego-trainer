from ego.testing import case

@case(
    args=(),
    expected=(7, 3, 10, 4, 3),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_ts01_trace():
    ...
