from ego.testing import case

@case(
    args=(),
    expected=(4, 1, 2, 8, 'поймано', False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_pt04_trace():
    ...
