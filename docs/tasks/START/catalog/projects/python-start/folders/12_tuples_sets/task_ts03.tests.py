from ego.testing import case

@case(
    args=((1, 2), 5),
    expected=(5, 2),
    description='обычный сдвиг',
    level='smoke',
)

@case(
    args=((0, 0), -3),
    expected=(-3, 0),
    description='из нуля в отрицательное',
    level='smoke',
)

@case(
    args=((4, 9), 4),
    expected=(4, 9),
    description='x не изменился',
    level='smoke',
)

@case(
    args=((7, -1), 0),
    expected=(0, -1),
    description='новое x равно нулю, y отрицательный',
    level='full',
)

@case(
    args=((10, 20), 30),
    expected=(30, 20),
    description='большие числа',
    level='full',
)
def task_ts03_move_x(point, new_x):
    ...
