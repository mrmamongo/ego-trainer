from ego.testing import case


@case(
    args=(),
    expected=(104, 110, 104, "x"),
    description='ответы на трассировку указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_er02_trace():
    ...
