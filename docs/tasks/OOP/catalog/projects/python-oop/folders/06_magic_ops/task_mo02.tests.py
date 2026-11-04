from ego.testing import case

@case(
    args=(),
    expected=(3, 'rock', 'pop', 'j', 'нет трека', 0),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_mo02_trace():
    ...
