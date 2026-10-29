from ego.testing import case

@case(
    args=(),
    expected=('нельзя', 1, 2, False, True, False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_dc03_trace():
    ...
