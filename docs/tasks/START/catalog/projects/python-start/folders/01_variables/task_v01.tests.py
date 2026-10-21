from ego.testing import case


@case(
    args=(),
    expected=(10, 4, 7, 4, 7, 1),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v01_trace():
    ...
