from ego.testing import case


@case(
    args=(),
    expected=(0, 4, 10, 15),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v03_trace():
    ...
