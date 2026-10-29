from ego.testing import case


@case(
    args=(),
    expected=(6, 4, 3, 5, 1, 6),
    description='стопка вызовов и результаты указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_ns01_trace():
    ...
