from ego.testing import case


@case(
    args=(),
    expected=("зачёт", 40),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v10_trace():
    ...
