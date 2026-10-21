from ego.testing import case


@case(
    args=(),
    expected=(220, 55, 200, False),
    description='значения и видимость переменной указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_fn02_trace():
    ...
