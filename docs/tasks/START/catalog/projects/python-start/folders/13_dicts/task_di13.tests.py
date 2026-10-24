from ego.testing import case

@case(
    args=(),
    expected=('Боря', 'dev', 2, 5, 3),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_di13_trace():
    ...
