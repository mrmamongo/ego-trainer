from ego.testing import case

@case(
    args=(),
    expected=(20, 15, 20, True, 19),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_cl02_trace():
    ...
