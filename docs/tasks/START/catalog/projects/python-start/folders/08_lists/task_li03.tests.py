from ego.testing import case

@case(
    args=(),
    expected=(13, 2, 8, 9, 0, 5),
    description='ответы на трассировку указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_li03_trace():
    ...
