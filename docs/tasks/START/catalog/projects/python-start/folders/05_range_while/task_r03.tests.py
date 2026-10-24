from ego.testing import case

@case(
    args=(),
    expected=(1, 3, 6, 10, 4),
    description='накопитель после каждого прохода и число проходов указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_r03_trace():
    ...
