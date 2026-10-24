from ego.testing import case

@case(
    args=(),
    expected=("red green  blue", 3, "red-green-blue", 4, -1, True),
    description="значения после трассировки указаны верно",
    level="smoke",
    hide_expected=True,
)
def task_s18_trace():
    ...
