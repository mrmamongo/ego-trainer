from ego.testing import case

@case(
    args=(),
    expected=(8, 3, 5, 3, 3),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_in03_lookup():
    ...
