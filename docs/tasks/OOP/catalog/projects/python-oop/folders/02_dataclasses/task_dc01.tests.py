from ego.testing import case

@case(
    args=(),
    expected=(True, False, 10, 3, False, "Item(name='Меч', qty=3)"),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_dc01_trace():
    ...
