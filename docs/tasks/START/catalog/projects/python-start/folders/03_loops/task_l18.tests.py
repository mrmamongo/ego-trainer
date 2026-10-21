from ego.testing import case


@case(
    args=(),
    expected=(4, 9, 9, 9, 9, 9),
    description='лучший на каждом проходе и итог указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_l18_trace():
    ...
