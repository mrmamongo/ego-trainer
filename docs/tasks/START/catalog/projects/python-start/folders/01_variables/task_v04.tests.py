from ego.testing import case


@case(
    args=(),
    expected=(3, 3, 10, 3),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v04_trace():
    ...
