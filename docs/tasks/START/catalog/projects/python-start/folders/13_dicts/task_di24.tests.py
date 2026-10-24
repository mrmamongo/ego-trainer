from ego.testing import case

@case(
    args=(),
    expected=('груши', 'киви', 'сливы', 'сливы', 'киви', 'яблоки'),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_di24_trace():
    ...
