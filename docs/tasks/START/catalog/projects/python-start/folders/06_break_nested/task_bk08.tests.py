from ego.testing import case

@case(
    args=(),
    expected=(9, 27, False, 4, 81),
    description='проходы while True и значение при break указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_bk08_trace():
    ...
