from ego.testing import case

@case(
    args=(),
    expected=("p", "h", "n", "t", 6, "o"),
    description="значения после трассировки указаны верно",
    level="smoke",
    hide_expected=True,
)
def task_s01_trace():
    ...
