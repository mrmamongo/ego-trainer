from ego.testing import case


@case(
    args=(),
    expected=(1, 1, 2, 2, 2),
    description='счётчик после каждого прохода и итог указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_l07_trace():
    ...
