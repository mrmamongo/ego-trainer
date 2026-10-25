from ego.testing import case

@case(
    args=("Аня;20\nБоря;30",),
    expected=None,
    description='все записи хорошие',
    level="smoke",
)

@case(
    args=("Аня;20\nБоря;abc\nВера;-1",),
    expected=(2, "не число"),
    description='первая плохая — вторая, остальные не смотрим',
    level="smoke",
)

@case(
    args=("Аня;20\n\nБоря",),
    expected=(3, "ожидается имя;возраст"),
    description='пустая строка считается в нумерации',
    level="smoke",
)

@case(
    args=(";20",),
    expected=(1, "пустое имя"),
    description='пустое имя',
    level="full",
)

@case(
    args=("Аня;20;5",),
    expected=(1, "ожидается имя;возраст"),
    description='лишняя часть',
    level="full",
)

@case(
    args=("",),
    expected=None,
    description='пустой текст',
    level="full",
)

@case(
    args=("Аня;151",),
    expected=(1, "больше 150"),
    description='слишком большой возраст',
    level="full",
)

@case(
    args=("\nАня;-3",),
    expected=(2, "меньше нуля"),
    description='отрицательный возраст после пустой строки',
    level="full",
)

@case(
    args=("  \nАня; 40 \n   ;5",),
    expected=(3, "пустое имя"),
    description='пробелы: имя из пробелов пустое, возраст с пробелами хороший',
    level="full",
    hide_expected=True,
)

@case(
    args=("Аня;0\nБоря;150",),
    expected=None,
    description='границы возраста допустимы',
    level="full",
    hide_expected=True,
)
def task_er17_first_error_line(text):
    ...
