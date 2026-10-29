from ego.testing import case

@case(
    args=(),
    expected=(3, 'щит', 'меч', True, False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_cl13_trace():
    ...
