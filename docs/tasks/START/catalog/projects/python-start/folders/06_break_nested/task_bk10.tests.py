from ego.testing import case

@case(
    args=(),
    expected=('none', 7, 'even', False, 6),
    description='результаты for-else с break и без него указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_bk10_trace():
    ...
