from ego.testing import case

@case(
    args=(),
    expected=("м.", "им..", "рим...", 6),
    description="значения после трассировки указаны верно",
    level="smoke",
    hide_expected=True,
)
def task_s02_trace():
    ...
