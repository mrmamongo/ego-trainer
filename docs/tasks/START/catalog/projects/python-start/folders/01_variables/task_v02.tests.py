from ego.testing import case


@case(
    args=(),
    expected=(5, 7, 21),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v02_trace():
    ...
