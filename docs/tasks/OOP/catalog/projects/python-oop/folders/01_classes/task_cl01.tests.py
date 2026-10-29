from ego.testing import case

@case(
    args=(),
    expected=(30, 25, 80, 'Орк', 105),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_cl01_trace():
    ...
