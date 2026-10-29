from ego.testing import case


@case(
    args=(),
    expected=("ru", "пусто", "-", 3, 1, 2),
    description='результаты вызовов и число шагов указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_ns06_trace():
    ...
