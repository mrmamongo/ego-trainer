from ego.testing import case

@case(
    args=(),
    expected=(3, 5, 8, 0),
    description='числа первого range и пустой второй range указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_r02_trace():
    ...
