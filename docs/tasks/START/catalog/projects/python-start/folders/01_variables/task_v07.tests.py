from ego.testing import case


@case(
    args=(),
    expected=("23", 5),
    description="таблица трассировки заполнена верно",
    level="smoke",
    hide_expected=True,
)
def task_v07_trace():
    ...
