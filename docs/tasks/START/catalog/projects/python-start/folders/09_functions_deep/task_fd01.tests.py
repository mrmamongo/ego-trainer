from ego.testing import case

@case(
    args=(),
    expected=(6, 13, 9, 2),
    description='значения после вызовов и число вызовов double указаны верно',
    level="smoke",
    hide_expected=True,
)

def task_fd01_trace():
    ...
