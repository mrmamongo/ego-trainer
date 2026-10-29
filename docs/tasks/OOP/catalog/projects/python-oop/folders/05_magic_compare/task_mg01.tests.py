from ego.testing import case

@case(
    args=(),
    expected=('Coin(5)', '5 монет', '5 монет', '[Coin(5)]', "Gem('рубин')", "Gem('рубин') и 5 монет"),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_mg01_trace():
    ...
