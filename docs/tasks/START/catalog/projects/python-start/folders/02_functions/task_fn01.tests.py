from ego.testing import case


@case(
    args=(),
    expected=(8, 16, 18),
    description='значения после вызовов функции указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_fn01_trace():
    ...
