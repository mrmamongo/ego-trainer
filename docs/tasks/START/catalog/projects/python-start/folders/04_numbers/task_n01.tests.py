from ego.testing import case


@case(
    args=(),
    expected=(10, "107", 3.5, 3),
    description='типы и значения указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_n01_trace():
    ...
