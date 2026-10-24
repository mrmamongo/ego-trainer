from ego.testing import case

@case(
    args=(),
    expected=(0, 1, 3, 4),
    description='значения i и число проходов указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_r01_trace():
    ...
