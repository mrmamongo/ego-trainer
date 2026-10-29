class Progress:
    """Готовый класс: полоса прогресса. Проценты можно задавать только от 0 до 100."""

    def __init__(self):
        self._percent = 0

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, value):
        if value < 0 or value > 100:
            raise ValueError("процент от 0 до 100")
        self._percent = value


def task_pr08_apply(steps):
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return [bar.percent, rejected]
    #   bar = Progress()
    #   rejected = rejected + 1
    #   for step in steps:
    #   except ValueError:
    #   rejected = 0
    #   try:
    #   bar.percent = step
    #
    return None  # собери тело функции из строк выше
