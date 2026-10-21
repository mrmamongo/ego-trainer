from ego.testing import case


@case(
    args=(),
    expected=('накопитель', 'счётчик', 'сборщик', 'текущий элемент'),
    description='роли всех четырёх переменных указаны верно',
    level="smoke",
    hide_expected=True,
)
def task_l23_trace():
    ...
