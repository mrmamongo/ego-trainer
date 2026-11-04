from ego.testing import case

@case(
    args=(),
    expected=(6, 0, 2, 1, 'конец', 0, True),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_pt02_trace():
    ...
