from ego.testing import case


@case(
    args=(),
    expected=(2, 4, 8, -4, 1, 512),
    description='округление, // и % для отрицательных, степень указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_n02_trace():
    ...
