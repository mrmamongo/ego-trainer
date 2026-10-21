from ego.testing import case


@case(
    args=(),
    expected=(50, 100, 150, 130, 0),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v13_trace():
    ...
