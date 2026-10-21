from ego.testing import case


@case(
    args=(),
    expected=(1, 2, 1, 2, 1, 1),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v09_trace():
    ...
