from ego.testing import case


@case(
    args=(),
    expected=(-2, 0, 0),
    description='результаты трёх вызовов указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_l13_trace():
    ...
