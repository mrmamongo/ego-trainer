from ego.testing import case

@case(
    args=(),
    expected=(5, 12, 'Грок', True, False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_in01_inherit():
    ...
