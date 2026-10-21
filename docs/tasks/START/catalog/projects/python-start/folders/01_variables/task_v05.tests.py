from ego.testing import case


@case(
    args=(),
    expected=(360, 5, 360),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v05_trace():
    ...
