from ego.testing import case

@case(
    args=(),
    expected=("pro", "gra", "prog", "ing", "pormig", ""),
    description="значения после трассировки указаны верно",
    level="smoke",
    hide_expected=True,
)
def task_s08_trace():
    ...
