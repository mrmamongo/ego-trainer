def task_l10_evens(numbers):
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return result
    #   if number % 2 == 0:
    #   result = []
    #   result.append(number)
    #   for number in numbers:
    #
    result = []
    for number in numbers:
        if number % 2 == 0:
            result.append(number)
    return result
