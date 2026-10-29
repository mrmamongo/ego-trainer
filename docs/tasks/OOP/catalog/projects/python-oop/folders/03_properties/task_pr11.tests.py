from ego.testing import case

@case(
    args=(),
    expected=('зарплата', 'запрет', 100, 120, 90),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_pr11_trace():
    ...
