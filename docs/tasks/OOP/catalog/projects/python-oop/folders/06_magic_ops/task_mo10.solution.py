class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)


def task_mo10_path(steps):
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return [total.x, total.y]
    #   for x, y in steps:
    #   step = Vector2(x, y)
    #   total = total + step
    #   total = Vector2(0, 0)
    #
    total = Vector2(0, 0)
    for x, y in steps:
        step = Vector2(x, y)
        total = total + step
    return [total.x, total.y]
