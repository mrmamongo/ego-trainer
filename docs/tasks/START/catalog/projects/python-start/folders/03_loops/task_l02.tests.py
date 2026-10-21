from ego.testing import case


@case(
    args=(),
    expected=(10, 30, 35, 35),
    description='накопитель после каждого прохода и итог указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_l02_trace():
    ...
