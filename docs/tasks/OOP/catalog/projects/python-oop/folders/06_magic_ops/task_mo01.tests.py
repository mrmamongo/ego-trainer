from ego.testing import case

@case(
    args=(),
    expected=(11, 22, 44, 1, 1, False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_mo01_trace():
    ...
