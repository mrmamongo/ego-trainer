from ego.testing import case


@case(
    args=(),
    expected=(2, 2, 2, 2),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v08_trace():
    ...
