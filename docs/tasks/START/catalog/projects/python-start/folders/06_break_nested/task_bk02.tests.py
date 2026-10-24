from ego.testing import case

@case(
    args=(),
    expected=(4, 9, 5, 2, 12),
    description='проходы, пропуски и итог при continue указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_bk02_trace():
    ...
