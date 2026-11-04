from ego.testing import case

@case(
    args=(),
    expected=(True, True, False, True, False, False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_in05_isinstance():
    ...
