from ego.testing import case


@case(
    args=(3, 4, 5),
    expected='разносторонний',
    description='все стороны разные',
    level="smoke",
)

@case(
    args=(5, 5, 5),
    expected='равносторонний',
    description='все стороны равны',
    level="smoke",
)

@case(
    args=(5, 5, 8),
    expected='равнобедренный',
    description='две равные стороны',
    level="smoke",
)

@case(
    args=(1, 2, 3),
    expected='не треугольник',
    description='сторона равна сумме двух других',
    level="smoke",
)

@case(
    args=(1, 1, 5),
    expected='не треугольник',
    description='сторона больше суммы двух других',
    level="full",
)

@case(
    args=(2, 3, 2),
    expected='равнобедренный',
    description='равны первая и третья',
    level="full",
)

@case(
    args=(10, 1, 1),
    expected='не треугольник',
    description='длинная первая сторона',
    level="full",
)

@case(
    args=(7, 10, 5),
    expected='разносторонний',
    description='ещё один разносторонний',
    level="full",
)
def task_fn16_triangle(a, b, c):
    ...
