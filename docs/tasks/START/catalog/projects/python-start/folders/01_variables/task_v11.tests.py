from ego.testing import case


@case(
    args=(),
    expected=(0, 1100, 50),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v11_trace():
    ...
