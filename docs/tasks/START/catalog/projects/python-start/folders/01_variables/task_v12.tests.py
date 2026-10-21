from ego.testing import case


@case(
    args=(),
    expected=(2, "z"),
    description="строка ошибки и имя переменной указаны верно",
    level="smoke",
    hide_expected=True,
)
def task_v12_trace():
    ...
