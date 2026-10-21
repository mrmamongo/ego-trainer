from ego.testing import case


@case(
    args=(),
    expected=(3, 8, 1),
    description='число проходов, значение на 2-м проходе и итог указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_l01_trace():
    ...
