from ego.testing import case

@case(
    args=(),
    expected=(7, 50, 7, 0, 5, 7, 5, 0, 12),
    description='цифры, остаток числа и сумма после каждого прохода указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_r12_trace():
    ...
