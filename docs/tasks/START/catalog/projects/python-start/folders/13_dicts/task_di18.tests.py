from ego.testing import case

@case(
    args=(),
    expected=('en', 'en', 2, True, False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_di18_trace():
    ...
