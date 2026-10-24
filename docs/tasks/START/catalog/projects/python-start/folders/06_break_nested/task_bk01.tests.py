from ego.testing import case

@case(
    args=(),
    expected=(4, 10, 3, -1, 10),
    description='проходы, number и total после break указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_bk01_trace():
    ...
