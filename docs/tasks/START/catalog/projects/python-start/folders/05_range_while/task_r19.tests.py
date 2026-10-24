from ego.testing import case

@case(
    args=(),
    expected=(70, 40, 10, 3, 4),
    description='значения x, число проходов и число проверок указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_r19_trace():
    ...
