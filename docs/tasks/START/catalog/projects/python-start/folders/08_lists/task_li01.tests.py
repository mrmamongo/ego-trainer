from ego.testing import case

@case(
    args=(),
    expected=(10, 40, 25, 35, 4),
    description='ответы на трассировку указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_li01_trace():
    ...
