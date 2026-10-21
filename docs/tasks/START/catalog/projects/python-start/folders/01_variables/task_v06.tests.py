from ego.testing import case


@case(
    args=(),
    expected=(5, 50, 20, 23),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v06_trace():
    ...
