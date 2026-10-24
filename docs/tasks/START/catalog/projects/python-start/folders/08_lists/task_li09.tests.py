from ego.testing import case

@case(
    args=(),
    expected=(5, 7, True, 2, 1),
    description='ответы на трассировку указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_li09_trace():
    ...
