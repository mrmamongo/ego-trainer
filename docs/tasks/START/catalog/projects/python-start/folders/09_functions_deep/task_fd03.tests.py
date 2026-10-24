from ego.testing import case

@case(
    args=(),
    expected=(220, 240, 205, 150, 10),
    description='результаты вызовов с умолчаниями и именами указаны верно',
    level="smoke",
    hide_expected=True,
)

def task_fd03_trace():
    ...
