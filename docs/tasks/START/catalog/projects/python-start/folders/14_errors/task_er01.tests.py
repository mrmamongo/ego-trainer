from ego.testing import case


@case(
    args=(),
    expected=(False, True, False, True, "ace"),
    description='ответы на трассировку указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_er01_trace():
    ...
