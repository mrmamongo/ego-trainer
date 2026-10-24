from ego.testing import case

@case(
    args=(),
    expected=(3, 10, 1, 5, 20),
    description='пары (i, j), счётчик и влияние break на внутренний цикл указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_bk13_trace():
    ...
