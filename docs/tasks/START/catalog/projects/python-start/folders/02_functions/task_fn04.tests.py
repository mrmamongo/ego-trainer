from ego.testing import case


@case(
    args=(),
    expected=(10, True, 10),
    description='экран, None и возвращённое значение указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_fn04_trace():
    ...
