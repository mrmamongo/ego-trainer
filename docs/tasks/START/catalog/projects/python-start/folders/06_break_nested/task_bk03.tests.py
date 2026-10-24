from ego.testing import case

@case(
    args=(),
    expected=(3, 2, 5, 4, 9),
    description='результаты break и continue на одном списке указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_bk03_trace():
    ...
