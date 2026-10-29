from ego.testing import case

@case(
    args=(),
    expected=('Привет, Аня', 'Пока, Боря', 15, 2, 'Пока, Вика', True),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_cm01_trace():
    ...
