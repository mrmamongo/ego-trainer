from ego.testing import case


@case(
    args=(),
    expected=(3, -2, 4, "outer"),
    description='ответы на трассировку указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_er07_trace():
    ...
