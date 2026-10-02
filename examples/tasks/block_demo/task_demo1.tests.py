from ego.testing import case

@case(
    args=(2, 3),
    expected=5,
    description='two positives',
)
@case(
    args=(0, 0),
    expected=0,
    description='zeros',
)
@case(
    args=(-1, 5),
    expected=4,
    description='negative + positive',
)
def task_demo1_add(a, b):
    ...
