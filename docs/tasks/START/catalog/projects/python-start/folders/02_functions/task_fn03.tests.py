from ego.testing import case


@case(
    args=(),
    expected=('A', 'A', 'B', 'C'),
    description='результаты вызовов grade указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_fn03_trace():
    ...
