from ego.testing import case

@case(
    args=(),
    expected=(101, 6, 100, 7, 100),
    description='значения при вызовах с глобальной и локальной total указаны верно',
    level="smoke",
    hide_expected=True,
)

def task_fd05_trace():
    ...
