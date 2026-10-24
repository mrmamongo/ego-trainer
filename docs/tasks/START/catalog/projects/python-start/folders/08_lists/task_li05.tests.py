from ego.testing import case

@case(
    args=(),
    expected=(3, 3, 4, 9, 1),
    description='ответы на трассировку указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_li05_trace():
    ...
