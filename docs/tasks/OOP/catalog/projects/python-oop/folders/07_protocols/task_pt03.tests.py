from ego.testing import case

@case(
    args=(),
    expected=(0, 1, 1, 2, 2, 0, 3, 'финиш', 'пусто'),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_pt03_trace():
    ...
