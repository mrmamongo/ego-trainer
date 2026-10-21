from ego.testing import case


@case(
    args=(),
    expected=(180, -10, 25),
    description='результаты вызовов discount указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_fn06_trace():
    ...
